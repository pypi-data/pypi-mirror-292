'''
Assetto Corsa Log Watcher.

Ideas and code from: https://github.com/kuralabs/logserver/blob/master/server/server.py
'''

import asyncio
import json
import logging
import re

import aiofiles

from ac_websocket_server.objects import DriverInfo, EnhancedJSONEncoder, LobbyEvent, ServerEvent, SessionEvent, Message, MessageType
from ac_websocket_server.observer import Notifier
from ac_websocket_server.task_logger import create_task

TAIL_DELAY = 1


class Watcher(Notifier):
    '''Represents a watcher for AC logfiles.
    Parses log files and sends messages to send_queue.'''

    def __init__(self, filename: str) -> None:
        '''Create Watcher instance for filename.'''

        self._logger = logging.getLogger('ac-ws.watcher')

        self._filename = filename

        self._readlines_task: asyncio.Task

        self._lobby_event = LobbyEvent()
        self._driver_event = DriverInfo()
        self._server_event = ServerEvent()
        self._session_event = SessionEvent()

        super().__init__()

    async def parse_lines(self, _file, lines):
        '''Parse lines of logfile and send messages to observer.'''
        # pylint: disable=invalid-name, pointless-string-statement

        for line in lines:

            '''Parse for server info - see tests/watcher_test.py for details.'''

            m = re.compile(
                r'^Assetto Corsa Dedicated Server (.*)').match(line)
            if m:
                self._server_event.version = m.group(1)
                self._server_event.msg = 'Assetto Corsa Dedicated Server starting'

            m = re.compile(
                r'^(\d{4}-\d{2}-\d{2} .*)$').match(line)
            if m:
                self._server_event.timestamp = m.group(1)

            m = re.compile(
                r'^CARS=(.*)').match(line)
            if m:
                await self.put(json.dumps(Message(type=MessageType.SERVER_EVENT,
                                                  body=self._server_event),
                                          cls=EnhancedJSONEncoder))
                continue

            '''Parse for session info - see tests/watcher_test.py for details.'''

            m = re.compile(
                r'^SENDING session name : (.*)').match(line)
            if m:
                self._session_event.type = m.group(1)
                if self._session_event.type == 'Qualification':
                    self._session_event.type = 'Qualify'
                    self._server_event.type = 'Qualify'
                self._session_event.msg = f'{self._session_event.type} session starting'

            m = re.compile(
                r'^SENDING session time : (.*)').match(line)
            if m:
                self._session_event.time = int(m.group(1))

            m = re.compile(
                r'^SENDING session laps : (.*)').match(line)
            if m:
                self._session_event.laps = int(m.group(1))
                await self.put(json.dumps(Message(type=MessageType.SESSION_EVENT,
                                                  body=self._session_event),
                                          cls=EnhancedJSONEncoder))
                continue

            '''Parse for driver info - see tests/watcher_test.py for details.'''

            m = re.compile(
                r'^NEW PICKUP CONNECTION from  (.*):(\d*)').match(line)
            if m:
                self._driver_event = DriverInfo()
                self._driver_event.host = m.group(1)
                self._driver_event.port = int(m.group(2))

            m = re.compile(
                r'^Looking for available slot by name for GUID (\d*) (.*)').match(line)
            if m:
                self._driver_event.guid = m.group(1)
                self._driver_event.car = m.group(2)

            m = re.compile(
                r'^Slot found at index (\d*)').match(line)
            if m:
                self._driver_event.slot = int(m.group(1))

            m = re.compile(
                r'^DRIVER: (.*) \[.*$').match(line)
            if m:
                self._driver_event.name = m.group(1)
                self._driver_event.msg = 'joining'
                await self.put(json.dumps(Message(type=MessageType.DRIVER_INFO,
                                                  body=self._driver_event),
                                          cls=EnhancedJSONEncoder))
                continue

            '''Parse for driver info - see tests/watcher_test.py for details.'''

            m = re.compile(
                r'^Clean exit, driver disconnected:  (.*) \[.*$').match(line)
            if m:
                self._driver_event = DriverInfo(name=m.group(1), msg='leaving')
                await self.put(json.dumps(Message(type=MessageType.DRIVER_INFO,
                                                  body=self._driver_event),
                                          cls=EnhancedJSONEncoder))
                continue

            '''
            CALLING http://93.57.10.21/lobby.ashx/register?name=SNRL+AC+%231&port=9601&tcp_port=9601&max_clients=12&track=rt_autodrom_most&cars=ks_mazda_mx5_cup&timeofday=-16&sessions=1,2,3&durations=7200,600,8&password=1&version=202&pickup=1&autoclutch=1&abs=1&tc=1&stability=0&legal_tyres=&fixed_setup=0&timed=0&extra=0&pit=0&inverted=0
            '''
            m = re.compile(
                r'^CALLING (.*)$').match(line)
            if m:

                self._lobby_event = LobbyEvent(url_register=m.group(1))
                await self.put(json.dumps(Message(type=MessageType.LOBBY_EVENT,
                                                  body=self._lobby_event),
                                          cls=EnhancedJSONEncoder))
                continue

            '''
            CONNECTED TO LOBBY
            '''
            m = re.compile(
                r'^CONNECTED TO LOBBY$').match(line)
            if m:
                self._lobby_event.connected = True
                if self._server_event.timestamp:
                    self._lobby_event.timestamp = self._server_event.timestamp
                await self.put(json.dumps(Message(type=MessageType.LOBBY_EVENT,
                                                  body=self._lobby_event),
                                          cls=EnhancedJSONEncoder))

            '''
            SENDING http://93.57.10.21/lobby.ashx/ping?session=2&timeleft=600&port=9601&clients=0&track=rt_autodrom_most&pickup=1
            '''
            m = re.compile(
                r'^SENDING (.*lobby.ashx\/ping.*)$').match(line)
            if m:
                self._lobby_event.url_ping = m.group(1)
                await self.put(json.dumps(Message(type=MessageType.LOBBY_EVENT,
                                                  body=self._lobby_event),
                                          cls=EnhancedJSONEncoder))
                continue
            '''
            ERROR,SERVER NOT REGISTERED WITH LOBBY - PLEASE RESTART
            ERROR - RESTART YOUR SERVER TO REGISTER WITH THE LOBBY
            '''

            m = re.compile(
                r'^ERROR.*REGISTER.*LOBBY$').match(line)
            if m:
                self._lobby_event.connected = False
                await self.put(json.dumps(Message(type=MessageType.LOBBY_EVENT,
                                                  body=self._lobby_event),
                                          cls=EnhancedJSONEncoder))

    async def readlines(self):
        '''Co-routine to be run as a task to read lines from logfile.'''
        # pylint: disable=invalid-name, logging-fstring-interpolation

        self._logger.debug(f'Started watching {self._filename}: ')

        async with aiofiles.open(self._filename, mode='r') as f:

            while True:
                line = await f.readline()
                if line:
                    await self.parse_lines(self._filename, [line])
                else:
                    await asyncio.sleep(TAIL_DELAY)

        self._logger.debug(f'Stopped watching {self._filename}: ')

    async def start(self):
        '''Start monitoring logfile'''

        self._readlines_task = create_task(self.readlines(),
                                           logger=self._logger,
                                           message='readlines() raised an exception')

    async def stop(self):
        '''Stop monitoring logfile'''

        self._readlines_task.cancel()

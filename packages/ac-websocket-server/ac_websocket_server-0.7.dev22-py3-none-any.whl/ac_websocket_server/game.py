'''Assetto Corsa Game Server Class'''

import asyncio
import configparser
import json
import logging
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from ac_websocket_server.child import ChildServer
from ac_websocket_server.configuration import ServerConfiguration
from ac_websocket_server.entries import EntryList
from ac_websocket_server.error import WebsocketsServerError
from ac_websocket_server.grid import Grid
from ac_websocket_server.objects import (DriverInfo, EntryInfo, SessionEvent)
from ac_websocket_server.lobby import Lobby
from ac_websocket_server.protocol import Protocol
from ac_websocket_server.watcher import Watcher


@dataclass
class GameServer(ChildServer):
    '''Represents an Assetto Corsa Server.'''
    # pylint: disable=logging-fstring-interpolation, invalid-name

    directory: str
    child_ini_file: str = field(default='cfg/server_cfg.ini')
    child_title: str = field(default='AC Server')
    child_short: str = field(default='AC Server')
    is_optional: bool = False

    version: str = field(default='n/a', init=False)
    timestamp: str = field(default='n/a', init=False)
    name: str = field(init=False)
    track: str = field(init=False)
    cars: str = field(init=False)
    http_port: int = field(init=False)
    tcp_port: int = field(init=False)
    udp_port: int = field(init=False)
    drivers: Dict[str, DriverInfo] = field(init=False)
    entries: Dict[int, EntryInfo] = field(init=False)
    sessions: Dict[str, SessionEvent] = field(init=False)
    lobby: Lobby = field(init=False)
    running: int = field(init=False, default=False)

    def __post_init__(self):

        super().__post_init__()

        self._logger = logging.getLogger('ac-ws.game')
        self._args = ()

        if os.path.exists(f'{self.directory}/acServer.py'):
            self._cwd = None
            self._exe = f'{self.directory}/acServer.py'
            self._hash = None
        else:
            self._cwd = self.directory
            if sys.platform == 'linux':
                self._exe = f'{self.directory}/acServer'
                self._hash = 'f781ddfe02e68adfa170b28d0eccbbdc'
            else:
                self._exe = f'{self.directory}/acServer.exe'
                self._hash = '357e1f1fd8451eac2d567e154f5ee537'

        self.entry_list_file_name = f'{self.directory}/cfg/entry_list.ini'
        self.entry_list_backup_name = f'{self.entry_list_file_name}.old'

        self.server_cfg_file_name = f'{self.directory}/{self.child_ini_file}'
        self.server_cfg_backup_name = f'{self.server_cfg_file_name}.old'

        self.cfg = configparser.ConfigParser()
        self.cfg.optionxform = str

        self.server_configuration: ServerConfiguration | None = None

        self._watcher_stdout: Watcher

        self.__setup()

    async def __configuration(self, args):
        '''Set server config options
        write
        '''

        if args[0] == 'write':
            try:
                self.server_configuration.write()
                await self.put(Protocol.success({'msg': f'Wrote {self.server_cfg_file_name}'}))
            except IOError as e:
                await self.put(Protocol.error({'msg': f'Failed to write {self.server_cfg_file_name}'}))
                raise WebsocketsServerError(e) from e
            
        self.parse_server_cfg()
        
        await self.__info()

    async def consumer(self, message_words: List[str], connection: id = None):
        '''Consume args destined for the server'''

        message_funcs = {'configuration': self.__configuration,
                         'drivers': self.__drivers,
                         'entries': self.__entries,
                         'info': self.__info,
                         'session': self.__session,
                         'sessions': self.__sessions,
                         'start': self.start,
                         'stop': self.stop,
                         'restart': self.restart}

        if message_funcs.get(message_words[0]):
            await message_funcs[message_words[0]](message_words[1:])
        else:
            await self.put(Protocol.error({'msg': f'Failed to parse {message_words}'}))


    async def __drivers(self, *_):
        '''Show game drivers info as part of a JSON reply'''
        await self.put(Protocol.success({'drivers': self.drivers}))

    async def __entries(self, *_):
        '''Show game entries info as part of a JSON reply'''
        await self.put(Protocol.success({'entries': self.entries}))

    async def __info(self, *_):
        '''Show game server info as a JSON string'''
        await self.put(Protocol.success({'server': self}))

    async def notify(self, notifier):
        '''Receive a notification of a new message from log watcher or lobby.'''

        message = await notifier.get(self)

        try:
            item = json.loads(message)

            if not item.get('type', None):
                if item.get('data', None):
                    await self.put(Protocol.success(item['data']))
                if item.get('error', None):
                    await self.put(Protocol.error(item['error']))
                return

            if item['type'] == 'LobbyEvent':
                await self.lobby.update(item['body'])
                item['body']['timestamp'] = self.lobby.since
                await self.put(Protocol.success({'lobby': {'event': item['body']}}))

            if item['type'] == 'ServerEvent':
                self.version = item['body']['version']
                self.timestamp = item['body']['timestamp']
                await self.put(Protocol.success({'server': {'event': item['body']}}))

            if item['type'] == 'DriverInfo' and item['body']['msg'] == 'joining':

                body = item['body']
                name = body['name']

                driver_info = DriverInfo()

                driver_info.name = name
                driver_info.host = body['host']
                driver_info.port = body['port']
                driver_info.car = body['car']
                driver_info.guid = body['guid']
                driver_info.ballast = body['ballast']
                driver_info.restrictor = body['restrictor']
                driver_info.msg = body['msg']

                self.drivers[driver_info.name] = driver_info

                self._logger.debug(f'Driver {name} joining')
                await self.put(Protocol.success({'driver': item['body']}))

            if item['type'] == 'DriverInfo' and item['body']['msg'] == 'leaving':
                body = item['body']
                name = body['name']
                del self.drivers[name]

                self._logger.debug(f'Driver {name} leaving')
                await self.put(Protocol.success({'driver': item['body']}))

            if item['type'] == 'SessionEvent':

                body = item['body']
                session_type = body['type']

                session_info = SessionEvent()

                for session in self.sessions:
                    self.sessions[session].active = False

                session_info.type = session_type
                session_info.laps = body['laps']
                session_info.time = body['time']
                session_info.active = True

                self.sessions[session_type] = session_info

                await self.put(Protocol.success({'session': {'event': session_info}}))

        except json.JSONDecodeError:
            pass

        # await self.put(message)

    def parse_entry_list(self):
        '''Parse entry list file and update attributes'''

        if not os.path.exists(self.entry_list_file_name):
            error_message = f'Missing entry_list.ini file in {self.directory}'
            self._logger.error(error_message)
            raise WebsocketsServerError(error_message)

        self.entry_list = EntryList(self.entry_list_file_name)
        self.entries = self.entry_list.entries

    def parse_server_cfg(self):
        '''Parse server config file and update attributes'''

        try:
            self.server_configuration = ServerConfiguration(
                self.server_cfg_file_name)

            self.name = self.server_configuration.name
            self.cars = self.server_configuration.cars
            self.track = self.server_configuration.track
            self.http_port = self.server_configuration.http_port
            self.tcp_port = self.server_configuration.tcp_port
            self.udp_port = self.server_configuration.udp_port
            self.sessions = self.server_configuration.sessions

        except WebsocketsServerError as e:
            raise WebsocketsServerError(e) from e

    def pre_start_hook(self):
        '''Parse and update status before start (for re-start post __init__)'''

        super().pre_start_hook()

        self._debug_transaction.open('game-start')
        self._debug_transaction.save_file(
            f'{self.directory}/{self.child_ini_file}')
        self._debug_transaction.save_file(
            f'{self.directory}/cfg/entry_list.ini')

        timestamp = '-' + datetime.now().strftime("%Y%m%d_%H%M%S")

        shutil.copy(f'{self.directory}/cfg/entry_list.ini',
                    f'{self.directory}/logs/acws/entry_list{timestamp}-{self.child_title}.ini')
        shutil.copy(f'{self.directory}/cfg/server_cfg.ini',
                    f'{self.directory}/logs/acws/server_cfg{timestamp}-{self.child_title}.ini')

        self.grid.restore()

        try:
            self.parse_server_cfg()
            self.parse_entry_list()
            self.grid.track = self.track
        except WebsocketsServerError as e:
            self._logger.error('Command failed - configuration error')
            raise e

    async def post_start_hook(self):

        super().post_start_hook()

        await self.put(Protocol.success(
            msg='Assetto Corsa server started'))

        self.lobby.subscribe(self)

        self._watcher_stdout = Watcher(self._logfile_stdout)
        self._watcher_stdout.subscribe(self)
        await self._watcher_stdout.start()

        self._debug_transaction.close()

    async def post_stop_hook(self):

        self.__setup()

        self._debug_transaction.open('game-stop')
        self._debug_transaction.save_file(
            f'{self.directory}/{self.child_ini_file}')
        self._debug_transaction.save_file(
            f'{self.directory}/cfg/entry_list.ini')

        await self.put(Protocol.success(
            msg='Assetto Corsa server stopped'))

        await self._watcher_stdout.stop()
        self._watcher_stdout.unsubscribe(self)

        self.lobby.unsubscribe(self)

    async def __sessions(self, *_):
        '''Show game sessions info as a JSON string'''
        await self.put(Protocol.success({'sessions': self.sessions}))

    async def __session(self, args):
        '''Set server config options
        server session session_name enabled | disabled | laps number_of_laps | time number_of_minutes
        '''

        try:
            session_name = str(args[0]).upper()
            if session_name not in ['PRACTICE', 'QUALIFY', 'RACE']:
                await self.put(Protocol.error({'msg': f'Invalid session name {session_name}'}))
                return
            option_name = str(args[1]).upper()
            if option_name not in ['ENABLE', 'DISABLE', 'LAPS', 'TIME']:
                await self.put(Protocol.error({'msg': f'Invalid option name {option_name}'}))
                return
            if option_name in ['LAPS', 'TIME']:
                option_value = args[2]
            else:
                option_value = None
        except IndexError:
            await self.put(Protocol.error({'msg': f'Failed to parse arguments to set command {args}'}))
            return

        try:

            match option_name:
                case 'DISABLE':
                    self.server_configuration.session_disable(session_name)
                    msg = f'Disabled {session_name}'
                case 'ENABLE':
                    self.server_configuration.session_enable(session_name)
                    msg = f'Enabled {session_name}'
                case 'LAPS':
                    self.server_configuration.session_modify(
                        session_name, laps=option_value)
                    msg = f'Set {session_name} to {option_value} laps'
                case 'TIME':
                    self.server_configuration.session_modify(
                        session_name, time=option_value)
                    msg = f'Set {session_name} to {option_value} minutes'

            await self.put(Protocol.success({'msg': msg}))

        except (IOError, OSError) as e:
            self._logger.error(e)
            await self.put(Protocol.error({'msg': f'Failed to update {self.server_cfg_file_name}'}))

    def __setup(self):
        '''(Re)set state'''

        self.drivers = {}
        self.entries = {}
        self.sessions = {}

        self.parse_server_cfg()
        self.parse_entry_list()

        self.grid = Grid(server_directory=self.directory,
                         track=self.track,
                         entry_list=self.entry_list)

        self.lobby = Lobby()

'''Assetto Corsa Lobby Class'''

import aiohttp
import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from ac_websocket_server.objects import EnhancedJSONEncoder, MessageType, LobbyEvent
from ac_websocket_server.observer import Notifier
from ac_websocket_server.protocol import Protocol


@dataclass
class Lobby(Notifier):
    '''Represents an Assetto Corsa Lobby'''

    connected: bool = field(default=False, init=False)
    since: datetime = field(default=None, init=False)
    url_register: str = field(default=None, init=False)
    url_ping: str = field(default=None, init=False)

    def __post_init__(self):

        super().__init__()

        self._logger = logging.getLogger('ac-ws.lobby')

    async def consumer(self, message_words: List[str], connection: id = None):
        '''Consume args destined for the lobby'''

        message_funcs = {'info': self._info,
                         'restart': self._restart}

        if message_funcs.get(message_words[0]):
            await message_funcs[message_words[0]]()

    async def _info(self):
        '''Send lobby information'''
        await self.put(Protocol.success({'lobby': self}))

    async def _restart(self):
        '''Re-start the lobby connection'''

        self._logger.info('Re-regestering to lobby')
        async with aiohttp.ClientSession() as session:

            if not self.url_register:
                msg = f'Cannot attempt to re-register with lobby as no URL is defined'
                self._logger.error(msg)
                await self.put(Protocol.error(msg=msg))
                return

            async with session.get(self.url_register) as resp:
                text = await resp.text()
                if resp.status == 200 and 'ERROR' not in text:
                    self._logger.info('Successfully re-registered to lobby')
                    self.connected = True
                    self.since = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z %Z")
                    lobby_event = LobbyEvent(
                        connected=self.connected,
                        timestamp=self.since,
                        url_register=self.url_register,
                        url_ping=self.url_ping)
                    await self.put(json.dumps(Message(type=MessageType.LOBBY_EVENT,
                                                      body=lobby_event),
                                              cls=EnhancedJSONEncoder))
                    # await self.put(Protocol.success(msg=text))

                else:
                    self._logger.error(
                        f'Failed attempt to re-register with lobby: {text}')
                    await self.put(Protocol.error(msg=text))

    async def update(self, lobby_event: LobbyEvent):
        '''Update lobby info'''

        if lobby_event['connected'] and not self.connected:
            self.connected = True
            self.since = lobby_event.get(
                'timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S %z %Z"))

        if not lobby_event['connected'] and self.connected:
            self.connected = False
            self.since = ''
            await self._restart()

        if lobby_event['url_register']:
            self.url_register = lobby_event['url_register']

        if lobby_event['url_ping']:
            self.url_ping = lobby_event['url_ping']

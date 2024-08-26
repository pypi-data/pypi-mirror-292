'''Assetto Corsa server.cfg helper Class'''

import configparser
import logging
import os
import shutil


from ac_websocket_server.objects import SessionEvent
from ac_websocket_server.error import WebsocketsServerError


class ServerConfiguration:
    '''The server configuration'''

    def __init__(self, file_name: str = None) -> None:
        '''
        Create a new ServerConfiguration.
        '''

        self._logger = logging.getLogger('ac-ws.configuration')

        self._cfg = configparser.ConfigParser()
        self._cfg.optionxform = str

        self._dirty = False

        self._file_name = file_name
        self._dir_name = os.path.dirname(self._file_name)

        if not os.path.exists(self._file_name):
            error_message = f'Missing server_cfg.ini file in {self._dir_name}'
            self._logger.error(error_message)
            raise WebsocketsServerError(error_message)

        try:
            self._cfg.read(self._file_name)
            if self._cfg.has_section('QUALIFICATION'):
                self.rename_section(self._cfg, 'QUALIFICATION', 'QUALIFY')
                self._cfg['QUALIFY']['NAME'] = 'Qualify'
        except configparser.Error as e:
            error_message = f'Unable to parse server_cfg.ini file in {self._dir_name}'
            raise WebsocketsServerError(error_message) from e

    @property
    def cars(self):
        '''Allowed cars'''
        return self._cfg['SERVER']['CARS']

    @cars.setter
    def cars(self, value):
        self._cfg['SERVER']['CARS'] = value
        self._dirty = True

    @property
    def http_port(self):
        '''HTTP port'''
        return self._cfg['SERVER']['HTTP_PORT']

    @property
    def name(self):
        '''Name of server'''
        return self._cfg['SERVER']['NAME']

    @name.setter
    def name(self, value):
        self._cfg['SERVER']['NAME'] = value
        self._dirty = True

    def rename_section(self, cfg, section_from, section_to):
        '''https://stackoverflow.com/questions/15069127/python-configparser-module-rename-a-section'''
        items = cfg.items(section_from)
        cfg.add_section(section_to)
        for item in items:
            cfg.set(section_to, item[0], item[1])
        cfg.remove_section(section_from)

    def session_disable(self, session_name: str):
        '''Disable a session'''

        session_name = session_name.upper()

        if self._cfg.has_section(session_name):
            self._cfg.remove_section(session_name)
            self._dirty = True

    def session_enable(self, session_name: str):
        '''Enable a session'''

        session_name = session_name.upper()

        if not self._cfg.has_section(session_name):
            self._cfg.add_section(session_name)
            self._cfg.set(session_name, 'NAME', session_name.capitalize())
            self._cfg.set(session_name, 'IS_OPEN', '1')
            if session_name == 'PRACTICE' or session_name == 'QUALIFY':
                self._cfg.set(session_name, 'TIME', '10')
            if session_name == 'RACE':
                self._cfg.set(session_name, 'LAPS', '10')
                self._cfg.set(session_name, 'WAIT_TIME', '60')
            self._dirty = True

    def session_modify(self, session_name: str,
                       laps: int | None = None,
                       time: int | None = None):
        '''Modify a session'''

        session_name = session_name.upper()

        if laps and session_name == 'RACE':
            self._cfg.set(session_name, 'LAPS', laps)
            self._cfg.remove_option(session_name, 'TIME')
            self._dirty = True
        if time:
            self._cfg.set(session_name, 'TIME', time)
            self._cfg.remove_option(session_name, 'LAPS')
            self._dirty = True

    @property
    def sessions(self):
        '''Dict of sessions'''

        sessions = {}

        for session in ['PRACTICE', 'QUALIFY', 'RACE']:
            if self._cfg.has_section(session):
                name = self._cfg[session].get('NAME').capitalize()
                time = self._cfg[session].get('TIME', 0)
                laps = self._cfg[session].get('LAPS', 0)
                sessions[name] = SessionEvent(name, laps=laps, time=time)

        return sessions

    @property
    def tcp_port(self):
        '''TCP port'''
        return self._cfg['SERVER']['TCP_PORT']

    @property
    def track(self):
        '''Name of track'''
        return self._cfg['SERVER']['TRACK']

    @track.setter
    def track(self, value):
        self._cfg['SERVER']['TRACK'] = value
        self._dirty = True

    @property
    def udp_port(self):
        '''UDP port'''
        return self._cfg['SERVER']['UDP_PORT']

    def write(self):
        '''Write the server config file'''
        # pylint: disable=logging-fstring-interpolation

        if not self._dirty:
            self._logger.error(f'{self._file_name} is not dirty')

        try:

            if not os.path.exists(self._file_name + '.old'):
                shutil.copy(self._file_name, self._file_name + '.old')
                self._logger.debug(
                    f'Created {self._file_name}.old before changes')

            with open(self._file_name, 'w', encoding='utf-8') as f:
                self._cfg.write(f, space_around_delimiters=False)
                self._dirty = False

        except (IOError, OSError) as e:
            error_message = f'Unable to write server_cfg.ini file in {self._dir_name}'
            self._logger.error(error_message)
            raise WebsocketsServerError(error_message) from e

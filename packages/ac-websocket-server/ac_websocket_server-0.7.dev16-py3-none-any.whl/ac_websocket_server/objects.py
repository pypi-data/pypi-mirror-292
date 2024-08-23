'''Assetto Corsa WebSockets Server Messages'''

from dataclasses import dataclass, is_dataclass, asdict
from datetime import date, datetime
from enum import Enum
import json
from typing import Union


class EnhancedJSONEncoder(json.JSONEncoder):
    '''
    Enhanced JSON encoder.

    Use as per:
    json.dumps(foo, cls=EnhancedJSONEncoder)

    https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses
    https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
    '''

    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


@dataclass
class DriverInfo:
    '''Represents a driver.'''
    name: str = ''
    host: str = ''
    port: int = 0
    car: str = ''
    guid: str = ''
    ballast: int = 0
    restrictor: int = 0
    slot: int = 0
    msg: str = ''


@dataclass(repr=False)
class EntryInfo:
    '''Represents an entry in the entry_list.ini file'''
    car_id: str
    model: str = ''
    skin: str = ''
    spectator_mode: int = 0
    drivername: str = ''
    team: str = ''
    guid: str = ''
    ballast: int = 0
    restrictor: int = 0

    def __post_init__(self):
        self.new_id = None

    def __repr__(self):
        '''Override __repr__ to match format of entry_list.ini'''

        if self.new_id is not None:
            result = "[CAR_" + str(self.new_id) + "]\n"
        else:
            result = "[" + str(self.car_id) + "]\n"
        result += "MODEL=" + self.model + "\n"
        result += "SKIN=" + self.skin + "\n"
        result += "SPECTATOR_MODE=" + str(self.spectator_mode) + "\n"
        result += "DRIVERNAME=" + self.drivername + "\n"
        result += "TEAM=" + self.team + "\n"
        result += "GUID=" + self.guid + "\n"
        result += "BALLAST=" + str(self.ballast) + "\n"
        result += "RESTRICTOR=" + str(self.restrictor) + "\n"
        result += "\n"

        return result


@ dataclass
class LobbyEvent:
    '''Represents information for the lobby.'''

    connected: bool = False
    timestamp: str = ''
    url_register: str = ''
    url_ping: str = ''


@ dataclass
class LogonInfo:
    '''Represents information for logon.'''

    username: str = ''
    password: str = ''
    protocol: str = ''


@ dataclass
class ServerEvent:
    '''Represents version information for a server.'''

    version: str = ''
    timestamp: str = ''
    msg: str = ''


@ dataclass
class SessionEvent:
    '''Represents an individual session in the AC game server'''

    type: str = ''
    laps: int = 0
    time: int = 0
    msg: str = ''
    active: bool = False


class MessageType(Enum):
    '''Allowable message types'''

    DRIVER_INFO = 'DriverInfo'
    LOBBY_EVENT = 'LobbyEvent'
    SERVER_EVENT = 'ServerEvent'
    SESSION_EVENT = 'SessionEvent'


MessageBody = Union[DriverInfo, ServerEvent, SessionEvent]


@ dataclass
class Message:
    '''Basic message structure'''
    type: MessageType
    body: MessageBody

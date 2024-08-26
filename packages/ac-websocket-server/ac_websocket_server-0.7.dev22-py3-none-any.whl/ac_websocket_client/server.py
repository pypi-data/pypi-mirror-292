#!/usr/bin/env python

'''Server UI'''

import re
import tkinter as tk
from typing import Dict

from ac_websocket_client.objects import (
    GriddedButton, GriddedEntry, GriddedFrame, GriddedLabel, TrafficLight)


class ServerUI(GriddedFrame):
    '''Server UI'''

    def __init__(self, parent):

        super().__init__(grid_row=1, grid_col=0, height_by=3.75)

        self.parent = parent

        self.configure_columns(1, 1, 4, 1, 1)

        self._buttons = {}
        self._fields = {}
        self._lights = {}

        grid_row = 0

        GriddedLabel(self, grid_row=grid_row, grid_col=0,
                     width=8, text="Game")

        GriddedLabel(self, grid_row=grid_row, grid_col=1,
                     width=8, text="started:")
        self._fields['started'] = tk.StringVar()
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['started'], state=tk.DISABLED)
        self._buttons['game'] = tk.StringVar(value='Start Game')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['game'],
                      command=lambda: self.parent.loop.create_task(self.parent.toggle_game()))
        self._lights['game'] = TrafficLight(self, row=grid_row, column=4)

        grid_row += 1

        self._fields['registered'] = tk.StringVar()
        GriddedLabel(self, grid_row=grid_row, grid_col=1,
                     width=8, text="registered:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['registered'], state=tk.DISABLED)
        self._lights['registered'] = TrafficLight(self, row=grid_row, column=4)
        self._buttons['lobby'] = tk.StringVar(value='(Re)register')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['lobby'],
                      command=lambda: self.parent.loop.create_task(self.parent.toggle_registration()))
        self._lights['lobby'] = TrafficLight(self, row=grid_row, column=4)

        grid_row += 1

        GriddedLabel(self, grid_row=grid_row,
                     grid_col=0, width=8, text="Config")

        self._fields['cfg'] = tk.StringVar()
        GriddedLabel(self, grid_row=grid_row, grid_col=1, width=8, text="cfg:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['cfg'], state=tk.DISABLED)
        self._buttons['save'] = tk.StringVar(value='Save .cfg')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['save'],
                      command=lambda: self.parent.loop.create_task(self.parent.save_configuration()))
        self._lights['save'] = TrafficLight(self, row=grid_row, column=4)

        grid_row += 1

        self._fields['name'] = tk.StringVar()
        GriddedLabel(self, grid_row=grid_row,
                     grid_col=1, width=8, text="name:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['name'], state=tk.DISABLED)

        grid_row += 1

        self._fields['track'] = tk.StringVar()
        GriddedLabel(self, grid_row=grid_row,
                     grid_col=1, width=8, text="track:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['track'], state=tk.DISABLED)

        grid_row += 1

        self._fields['cars'] = tk.StringVar()
        GriddedLabel(self, grid_row=grid_row,
                     grid_col=1, width=8, text="cars:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['cars'], state=tk.DISABLED)

        self._buttons['sessions'] = {}
        self._fields['sessions'] = {}
        self._lights['sessions'] = {}

        grid_row += 1

        self._fields['sessions']['Practice'] = tk.StringVar()
        self._fields['sessions']['Practice'].trace_add(
            'write', self._trace_sessions)
        GriddedLabel(self, grid_row=grid_row, grid_col=1,
                     width=8, text="practice:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['sessions']['Practice'])
        self._buttons['sessions']['Practice'] = tk.StringVar(value='Enable')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['sessions']['Practice'],
                      command=lambda: self.parent.loop.create_task(self._handle_session_button('Practice')))
        self._lights['sessions']['Practice'] = TrafficLight(
            self, row=grid_row, column=4)

        grid_row += 1

        self._fields['sessions']['Qualify'] = tk.StringVar()
        self._fields['sessions']['Qualify'].trace_add(
            'write', self._trace_sessions)
        GriddedLabel(self, grid_row=grid_row, grid_col=1,
                     width=8, text="qualify:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['sessions']['Qualify'])
        self._buttons['sessions']['Qualify'] = tk.StringVar(value='Enable')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['sessions']['Qualify'],
                      command=lambda: self.parent.loop.create_task(self._handle_session_button('Qualify')))
        self._lights['sessions']['Qualify'] = TrafficLight(
            self, row=grid_row, column=4)

        grid_row += 1

        self._fields['sessions']['Race'] = tk.StringVar()
        self._fields['sessions']['Race'].trace_add(
            'write', self._trace_sessions)
        GriddedLabel(self, grid_row=grid_row, grid_col=1,
                     width=8, text="race:")
        GriddedEntry(self, grid_row=grid_row, grid_col=2,
                     textvariable=self._fields['sessions']['Race'])
        self._buttons['sessions']['Race'] = tk.StringVar(value='Enable')
        GriddedButton(self, grid_row=grid_row, grid_col=3,
                      textvariable=self._buttons['sessions']['Race'],
                      command=lambda: self.parent.loop.create_task(self._handle_session_button('Race')))
        self._lights['sessions']['Race'] = TrafficLight(
            self, row=grid_row, column=4)

        self.update_ui()

    async def _handle_session_button(self, session: str):
        '''Handle session button presses for both 'Apply' and Enable/Disable'''

        if self._buttons['sessions'][session].get() == 'Apply':

            session_details = self._parse_session_description(
                self._fields['sessions'][session].get())
            if session_details.get('laps', None):
                session_type = 'laps'
                session_value = session_details['laps']
            if session_details.get('time', None):
                session_type = 'time'
                session_value = session_details['time']

            await self.parent.update_session(session,
                                             session_type,
                                             session_value)

        else:

            await self.parent.toggle_session(session)

    def _parse_session_description(self, description: str) -> Dict[str, int]:
        '''Parse the session description and return a dictionary '''

        result = {}

        m = re.compile(r'^(\d*) (\S*)$').match(description)
        if m:
            session_value = m.group(1)
            session_type = m.group(2)
        if session_type == 'laps':
            result['laps'] = int(session_value)
        if session_type == 'minutes':
            result['time'] = int(session_value)

        return result

    def _trace_sessions(self, *args):
        '''Update the parent with updated values'''

        for session in ('Practice', 'Qualify', 'Race'):

            if old_session := self.parent.sessions.get(session, None):
                old_laps = int(old_session['laps'])
                old_time = int(old_session['time'])
            else:
                old_laps = None
                old_time = None

            m = re.compile(
                r'^(\d*) (\S*)$').match(self._fields['sessions'][session].get())
            if m:
                new_value = m.group(1)
                if new_value != '':
                    new_value = int(new_value)
                new_type = m.group(2)
                if new_type == 'laps' and old_laps != new_value:
                    self._buttons['sessions'][session].set('Apply')
                if new_type == 'minutes' and old_time != new_value:
                    self._buttons['sessions'][session].set('Apply')

    def update_ui(self):
        '''Update the UI with the contents of the parent.server'''

        self._fields['cfg'].set(self.parent.server.get('child_ini_file', ''))
        self._fields['name'].set(self.parent.server.get('name', ''))
        self._fields['track'].set(self.parent.server.get('track', ''))
        self._fields['cars'].set(self.parent.server.get('cars', ''))

        if self.parent.states.is_connected:

            if self.parent.states.is_started:
                self._fields['started'].set(
                    self.parent.server.get('timestamp', None))
                self._buttons['game'].set('Stop Game')
                self._lights['game'].green()
            else:
                self._fields['started'].set('n/a')
                self._buttons['game'].set('Start Game')
                self._lights['game'].red()

            if self.parent.states.is_registered:
                self._fields['registered'].set(
                    self.parent.lobby.get('since', ''))
                self._buttons['lobby'].set('Re-register')
                self._lights['lobby'].green()
            else:
                self._fields['registered'].set('n/a')
                self._buttons['lobby'].set('Register')
                self._lights['lobby'].red()

        else:

            self._fields['started'].set('')
            self._lights['game'].gray()
            self._fields['registered'].set('')
            self._lights['lobby'].gray()

        if self.parent.states.cfg_needs_saving:
            self._lights['save'].red()
        else:
            self._lights['save'].gray()

        for session in ('Practice', 'Qualify', 'Race'):
            self._buttons['sessions'][session].set('Enable')
            self._fields['sessions'][session].set('')
            self._lights['sessions'][session].gray()

        if sessions := self.parent.sessions:
            for session_type in sessions:
                if session_type in ('Practice', 'Qualify', 'Race'):
                    self._buttons['sessions'][session_type].set('Disable')
                    session_active = sessions[session_type]['active']
                    if session_active:
                        self._lights['sessions'][session_type].green()
                    else:
                        self._lights['sessions'][session_type].gray()
                    if sessions[session_type]['laps'] == 0:
                        session_description = f'{str(sessions[session_type]["time"])} minutes'
                    else:
                        session_description = f'{str(sessions[session_type]["laps"])} laps'
                    self._fields['sessions'][session_type].set(
                        session_description)

        self.parent.loop.create_task(self._update_ui_async())

    async def _update_ui_async(self):
        '''Update async parts of UI'''
        if self.parent.states.cfg_needs_reload:
            self._fields['cfg'].set(self.parent.server.get(
                'child_ini_file', '') + '- needs server reload')
            await self._lights['save'].flash(start=True)
        else:
            await self._lights['save'].flash(stop=True)

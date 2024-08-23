#!/usr/bin/env python

'''Tracker UI'''

import tkinter as tk

from ac_websocket_client.objects import (
    GriddedButton, GriddedEntry, GriddedFrame, GriddedLabel, TrafficLight)


class TrackerUI(GriddedFrame):
    '''Tracker UI'''

    def __init__(self, parent):

        super().__init__(grid_row=2, grid_col=0, height_by=0.5)

        self.parent = parent

        self.configure_columns(1, 1, 4, 1, 1)

        GriddedLabel(self, grid_row=0,
                     grid_col=0, width=8, text="Tracker")
        GriddedLabel(self, grid_row=0,
                     grid_col=1, width=8, text="started:")

        self._field = tk.StringVar()
        GriddedEntry(self, grid_row=0, grid_col=2,
                     textvariable=self._field, state=tk.DISABLED)

        self._button = tk.StringVar(value='Start Tracker')
        GriddedButton(self, grid_row=0, grid_col=3,
                      textvariable=self._button,
                      command=lambda: self.parent.loop.create_task(self.parent.toggle_tracker()))
        self._light = TrafficLight(self, row=0, column=4)

        self.update_ui()

    def update_ui(self):
        '''Update the UI based on states'''

        if self.parent.states.is_tracking:
            self._light.green()
            if timestamp := self.parent.tracker.get('timestamp', None):
                self._field.set(timestamp)
            else:
                self._field.set('')
            self._button.set('Stop Tracker')
        else:
            self._light.red()
            self._field.set('n/a')
            self._button.set('Start Tracker')

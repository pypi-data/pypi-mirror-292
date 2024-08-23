#!/usr/bin/env python

'''Connection UI'''

import tkinter as tk

from ac_websocket_client.objects import (
    GriddedButton, GriddedEntry, GriddedFrame, GriddedLabel, TrafficLight)


class ConnectionUI(GriddedFrame):
    '''Connection UI'''

    def __init__(self, parent):

        super().__init__(grid_row=0, grid_col=0, height_by=0.5)

        self.parent = parent

        self.configure_columns(1, 1, 4, 1, 1)

        GriddedLabel(self, grid_row=0, grid_col=0, width=8, text="ACWS")
        GriddedLabel(self, grid_row=0, grid_col=1, width=8, text="url:")

        self.input = tk.StringVar()
        if self.parent.url:
            self.input.set(self.parent.url)

        self.entry = GriddedEntry(self, grid_row=0, grid_col=2,
                                  textvariable=self.input
                                  )
        self.entry.bind('<Return>', self._async_toggle_connection)
        self.entry.bind('<KeyRelease>', self._update_url)

        self.button = tk.StringVar(value='Connect')
        GriddedButton(self, grid_row=0, grid_col=3,
                      textvariable=self.button,
                      command=lambda: parent.loop.create_task(self.parent.toggle_connection()))

        self.light = TrafficLight(self, row=0, column=4)
        self.light.gray()

        self.update_ui()

    def _async_toggle_connection(self, _event):
        '''Connect to the websocket server'''
        self.parent.loop.create_task(self.parent.toggle_connection())

    def update_ui(self):
        '''Update the UI based on connection status'''

        self.input.set(self.parent.url)

        if self.parent.states.is_connected:
            self.button.set('Disconnect')
            self.light.green()
        else:
            self.button.set('Connect')
            self.light.red()

    def _update_url(self, _event):
        self.parent.url = self.input.get()

#!/usr/bin/env python

'''Driver UI'''

import tkinter as tk
from tkinter import ttk

from ac_websocket_client.objects import (
    GriddedButton, GriddedEntry, GriddedFrame, GriddedLabel, TrafficLight)


class DriverUI(GriddedFrame):
    '''Driver UI'''

    REORDER_OPTIONS = [
        'n/a',
        "Starting",
        "Finishing",
        "Reversed"
    ]

    def __init__(self, parent):

        super().__init__(grid_row=3, grid_col=0, height_by=4.5)

        self.parent = parent

        self.configure_columns(1, 1, 4, 1, 1)

        self._buttons = {}
        self._entries = {}
        self._lights = {}
        self._slots = ['n/a']

        GriddedLabel(self, grid_row=0, grid_col=0, width=8, text="Drivers")

        self._entry = tk.StringVar()
        GriddedEntry(self, grid_row=0, grid_col=2,
                     textvariable=self._entry, state=tk.DISABLED)

        GriddedLabel(self, grid_row=0, grid_col=1,
                     width=8, text="ini:")

        self._buttons['save'] = tk.StringVar(value='Save .ini')
        GriddedButton(self, grid_row=0, grid_col=3,
                      textvariable=self._buttons['save'],
                      command=lambda: self.parent.loop.create_task(self.parent.update_grid(write=True)))
        self._lights['save'] = TrafficLight(self, row=0, column=4)
        self._lights['save'].gray()

        GriddedLabel(self, grid_row=1, grid_col=1,
                     width=8, text="order by:")

        self._order_by = tk.StringVar()
        self._order_options = ttk.OptionMenu(
            self, self._order_by, *DriverUI.REORDER_OPTIONS)
        self._order_options.grid(row=1, column=2, padx=15, sticky='ew')
        self._order_by.set('n/a')

        GriddedButton(self, grid_row=1, grid_col=3,
                      text='Modify order', width=10,
                      command=lambda: self.parent.loop.create_task(self._upgrade_grid()))

        GriddedLabel(self, grid_row=2, grid_col=1,
                     width=8, text="slot:")

        self._slot_chosen = tk.StringVar()
        self._slot_options = ttk.OptionMenu(
            self, self._slot_chosen, *self._slots, command=self._update_slots)
        self._slot_options.grid(row=2, column=2, padx=15, sticky='ew')
        self._slot_chosen.set('n/a')

        GriddedButton(self, grid_row=2, grid_col=3,
                      text='Modify Slot', width=10,
                      command=lambda: self.parent.loop.create_task(self._not_implemented()))

        GriddedLabel(self, grid_row=3, grid_col=1,
                     width=8, text="car_id:")
        self._entries['car_id'] = tk.StringVar()
        GriddedEntry(self, grid_row=3, grid_col=2,
                     textvariable=self._entries['car_id'])

        GriddedLabel(self, grid_row=4, grid_col=1,
                     width=8, text="model:")
        self._entries['model'] = tk.StringVar()
        GriddedEntry(self, grid_row=4, grid_col=2,
                     textvariable=self._entries['model'])

        GriddedLabel(self, grid_row=5, grid_col=1,
                     width=8, text="guid:")
        self._entries['guid'] = tk.StringVar()
        GriddedEntry(self, grid_row=5, grid_col=2,
                     textvariable=self._entries['guid'])

        GriddedLabel(self, grid_row=6, grid_col=1,
                     width=8, text="drivername:")
        self._entries['drivername'] = tk.StringVar()
        GriddedEntry(self, grid_row=6, grid_col=2,
                     textvariable=self._entries['drivername'])

        GriddedLabel(self, grid_row=7, grid_col=1,
                     width=8, text="team:")
        self._entries['team'] = tk.StringVar()
        GriddedEntry(self, grid_row=7, grid_col=2,
                     textvariable=self._entries['team'])

        GriddedLabel(self, grid_row=8, grid_col=1,
                     width=8, text="skin:")
        self._entries['skin'] = tk.StringVar()
        GriddedEntry(self, grid_row=8, grid_col=2,
                     textvariable=self._entries['skin'])

        GriddedLabel(self, grid_row=9, grid_col=1,
                     width=8, text="ballast:")
        self._entries['ballast'] = tk.StringVar()
        GriddedEntry(self, grid_row=9, grid_col=2,
                     textvariable=self._entries['ballast'])

        GriddedLabel(self, grid_row=10, grid_col=1,
                     width=8, text="restrictor:")
        self._entries['restrictor'] = tk.StringVar()
        GriddedEntry(self, grid_row=10, grid_col=2,
                     textvariable=self._entries['restrictor'])

        self.update_ui()

    async def _upgrade_grid(self):

        match self._order_by.get():
            case "Starting":
                await self.parent.update_grid(by_starting=True)
            case "Finishing":
                await self.parent.update_grid(by_finishing=True)
            case "Reversed":
                await self.parent.update_grid(by_reversed=True)

        self.parent.states.ini_needs_saving = True

        self.update_ui()

    def _update_slots(self, slot):

        if slot != 'n/a':
            if entry := self.parent.entries.get(slot, None):
                self._entries['car_id'].set(entry['car_id'])
                self._entries['model'].set(entry['model'])
                self._entries['drivername'].set(entry['drivername'])
                self._entries['guid'].set(entry['guid'])
                self._entries['team'].set(entry['team'])
                self._entries['skin'].set(entry['skin'])
                self._entries['ballast'].set(entry['ballast'])
                self._entries['restrictor'].set(entry['restrictor'])
        else:
            self._entries['car_id'].set('')
            self._entries['model'].set('')
            self._entries['drivername'].set('')
            self._entries['guid'].set('')
            self._entries['team'].set('')
            self._entries['skin'].set('')
            self._entries['ballast'].set('')
            self._entries['restrictor'].set('')

    def update_ui(self):
        '''Update the UI based on states'''

        if self.parent.states.is_connected:

            self._slots = []
            for key in self.parent.entries:
                self._slots.append(key)

            self._slot_options.set_menu(0, *self._slots)

            if self.parent.states.ini_needs_saving:
                self._lights['save'].red()
            else:
                self._lights['save'].gray()

        else:

            self._order_by.set('n/a')
            self._slot_chosen.set('n/a')
            self._update_slots('n/a')

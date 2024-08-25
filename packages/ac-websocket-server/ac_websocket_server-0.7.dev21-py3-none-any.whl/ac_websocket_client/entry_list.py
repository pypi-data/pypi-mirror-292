#!/usr/bin/env python

'''Assetto Corsa Websockets App Entry List'''

import asyncio
import tkinter as tk
from tkinter import ttk
from typing import Optional
import websockets

from ac_websocket_client.app import App
from ac_websocket_client.objects import (
    FRAME_X, FRAME_Y,
    GriddedButton, GriddedFrame, GriddedLabel, GriddedTreeview,
    TrafficLight)


class EntryList(tk.Tk):
    '''Wrapper class for Tk app Entry List'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(width=FRAME_X, height=FRAME_Y)
        self.title("entry_list.ini")

        self.websocket = None

        self.entries = {}
        self.entries_saved_traffic_light: Optional[TrafficLight] = None

        entries_frame = GriddedFrame(grid_row=3, grid_col=0, height_by=3)
        entries_frame.configure_columns(1, 1, 1, 1, 1, 1, 1)

        GriddedLabel(entries_frame, grid_row=0,
                     grid_col=0, width=8, text="Grid")
        GriddedButton(entries_frame, grid_row=0, grid_col=3,
                      text='Order 1..n', width=10,
                      command=lambda: self.loop.create_task(self._set_grid(by_finishing=True)))
        GriddedButton(entries_frame, grid_row=0, grid_col=4,
                      text='Order n..1', width=10,
                      command=lambda: self.loop.create_task(self._set_grid(by_reverse=True)))
        GriddedButton(entries_frame, grid_row=0, grid_col=5,
                      text='Show', width=10,
                      command=lambda: self.loop.create_task(self._set_grid()))
        GriddedButton(entries_frame, grid_row=0, grid_col=6,
                      text='Save', width=10,
                      command=lambda: self.loop.create_task(self._set_grid(write=True)))

        self.entries_saved_traffic_light = TrafficLight(
            entries_frame, row=0, column=7)
        self.entries_saved_traffic_light.gray()

        self.entry_tree = GriddedTreeview(entries_frame, 1, 0, grid_span=8)
        self.entry_tree.add_columns('Name', 'GUID', 'Car', 'Ballast',
                                    'Restrictor', 'Position', 'Connected')
        self.entry_tree.set_widths(190, 80, 190, 80, 80, 80, 80)

        self.focus()

    async def _set_grid(self, by_finishing: bool = None, by_reverse: bool = None, write: bool = None):
        '''Set the grid order'''

        if self.states.is_connected:
            if by_finishing:
                await self.websocket.send('grid finish')
                return
            if by_reverse:
                await self.websocket.send('grid reverse')
                return
            if write:
                await self.websocket.send('grid save')
                return
            await self.websocket.send('grid entries')
        else:
            await self.consumer_queue.put(Protocol.error(msg='Not connected to ACWS server'))

    def update_entries(self, entries):
        '''Update the entries table'''
        # pylint: disable=consider-using-dict-items

        self.entries = entries

        self.entry_tree.delete(*self.entry_tree.get_children())
        for key in self.entries:
            self.entry_tree.insert('', tk.END,
                                   values=(self.entries[key]['drivername'],
                                           self.entries[key]['guid'],
                                           self.entries[key]['model'],
                                           self.entries[key]['ballast'],
                                           self.entries[key]['restrictor'],
                                           str(key + 1),
                                           self.entries[key]['connected']))

#!/usr/bin/env python

'''Console UI'''

import textwrap
import tkinter as tk

from ac_websocket_client.objects import (
    CONSOLE_X, GriddedButton, GriddedEntry, GriddedFrame,
    GriddedLabel, GriddedListbox, GriddedText, TrafficLight)


class ConsoleUI(GriddedFrame):
    '''Console UI'''

    ENABLE_WORDWRAP = False

    def __init__(self, parent):

        super().__init__(grid_row=4, grid_col=0, height_by=3.25)

        self.parent = parent

        self.configure_columns(1, 1, 4, 1, 1)

        GriddedLabel(self, grid_row=0, grid_col=0, width=8, text="Console")
        GriddedLabel(self, grid_row=0, grid_col=1, width=8, text="command:")

        self._field = tk.StringVar()
        self.entry = GriddedEntry(self, grid_row=0, grid_col=2,
                                  textvariable=self._field)
        self.entry.bind('<Return>', self._async_send_command)

        self._button = tk.StringVar(value='Send')
        GriddedButton(self, grid_row=0, grid_col=3,
                      textvariable=self._button,
                      command=lambda: self.parent.loop.create_task(self.parent.send_command()))

        self._light = TrafficLight(self, row=0, column=4)
        self._light.gray()

        self._listbox = GriddedListbox(
            self, grid_row=1, grid_col=0, grid_span=5)

        self.update_ui()

    def _async_send_command(self, _event):
        '''Send command to ACWS server'''
        self.parent.loop.create_task(self.parent.send_command())

    def input(self):
        '''Return command input to be sent to ACWS server'''
        return self._field.get()

    def output(self, timestamp: str, lines: str, fg='Black'):
        '''Send command output to console.'''

        indent = '.' * len(timestamp)
        output_fmt = {'fg': fg}

        for input_line in lines.splitlines():
            output_lines = f'{timestamp}: {input_line}\n'
            if ConsoleUI.ENABLE_WORDWRAP:
                for line in textwrap.wrap(output_lines,
                                          width=CONSOLE_X,
                                          subsequent_indent=indent):
                    self._listbox.insert(tk.END, line)
                    self._listbox.itemconfig(tk.END, output_fmt)
            else:
                self._listbox.insert(tk.END, output_lines)
                self._listbox.itemconfig(tk.END, output_fmt)

        self.update_ui()

    def update_ui(self):
        '''Update the UI'''

        self._listbox.yview(tk.END)

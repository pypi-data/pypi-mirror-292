#!/usr/bin/env python

'''Assetto Corsa Websockets App Objects'''

import asyncio
import tkinter as tk
from tkinter import ttk

APP_TITLE = 'ACWS Client'
BUTTON_X = 10
COLUMN_X = 50
CONSOLE_X = 86
CONSOLE_Y = 15
ENTRY_X = 40
FRAME_X = 800
FRAME_Y = 100
LABEL_X = 8
PAD_X = 10
PAD_Y = 5


class GriddedButton(ttk.Button):
    '''Button in a grid'''

    def __init__(self, parent, grid_row: int, grid_col: int,
                 width: int = BUTTON_X, **kwargs):

        super().__init__(parent, width=width, **kwargs)

        self.grid_propagate(False)
        self.grid(row=grid_row, column=grid_col, padx=PAD_X, pady=PAD_Y)


class GriddedEntry(ttk.Entry):
    '''Entry in a grid'''

    def __init__(self, parent,
                 grid_row: int, grid_col: int,
                 width: int = ENTRY_X, **kwargs):

        super().__init__(parent, width=width, foreground='black', **kwargs)

        self.grid_propagate(False)
        self.grid(row=grid_row, column=grid_col, padx=PAD_X, pady=PAD_Y)


class GriddedFrame(ttk.Frame):
    '''Frame inside a Grid'''

    def __init__(self, grid_row: int, grid_col: int,
                 height_by: float = 1, width_by: float = 1, **kwargs):

        super().__init__(height=FRAME_Y * height_by,
                         width=FRAME_X * width_by, **kwargs)

        self.grid_propagate(False)
        self.grid(row=grid_row, column=grid_col, padx=PAD_X, pady=PAD_Y)

    def configure_columns(self, *weights):
        '''Helper function to configure column weights'''
        i = 0
        for weight in weights:
            self.columnconfigure(i, weight=weight)
            i += 1

    def configure_rows(self, *weights):
        '''Helper function to configure row weights'''
        i = 0
        for weight in weights:
            self.rowconfigure(i, weights=weight)
            i += 1


class GriddedLabel(ttk.Label):
    '''Label inside a Grid'''

    def __init__(self, parent, grid_row: int, grid_col: int, width: int = LABEL_X, **kwargs):

        super().__init__(parent, width=width, **kwargs)

        self.grid_propagate(False)
        self.grid(row=grid_row, column=grid_col, padx=PAD_X, pady=PAD_Y)


class GriddedListbox(tk.Listbox):
    '''Listbox in a grid'''

    def __init__(self, parent, grid_row: int, grid_col: int,
                 grid_span: int = 1, **kwargs):

        super().__init__(parent, height=CONSOLE_Y, width=CONSOLE_X, **kwargs)

        scrollbar = tk.Scrollbar(parent, orient='vertical')
        scrollbar.config(command=self.yview)

        self.config(yscrollcommand=scrollbar.set)

        self.grid(row=grid_row, column=grid_col,
                  columnspan=grid_span, padx=PAD_X, pady=PAD_Y)
        scrollbar.grid(row=grid_row, column=grid_span-1, sticky='ns')


class GriddedText(tk.Text):
    '''Text in a gride'''

    def __init__(self, parent, grid_row: int, grid_col: int,
                 grid_span: int = 1, **kwargs):

        super().__init__(parent,
                         height=CONSOLE_Y * 75,
                         width=CONSOLE_X * 75,
                         wrap='word', **kwargs)

        scrollbar = tk.Scrollbar(parent, orient='vertical')
        scrollbar.config(command=self.yview)

        self.config(yscrollcommand=scrollbar.set)

        self.grid(row=grid_row, column=grid_col,
                  columnspan=grid_span, padx=PAD_X, pady=PAD_Y)
        scrollbar.grid(row=grid_row, column=grid_span-1, sticky='ns')


class GriddedTreeview(ttk.Treeview):
    '''Treeview in a grid'''

    def __init__(self, parent, grid_row: int, grid_col: int,
                 grid_span: int = 1, **kwargs):

        super().__init__(parent, height=CONSOLE_Y - 2, show='headings', **kwargs)

        scrollbar = tk.Scrollbar(parent, orient='vertical')
        scrollbar.config(command=self.yview)

        self.config(yscrollcommand=scrollbar.set)

        self.grid(row=grid_row, column=grid_col,
                  columnspan=grid_span, padx=PAD_X, pady=PAD_Y)
        scrollbar.grid(row=grid_row, column=grid_span-1, sticky='ns')

        self._columns = ()

    def add_columns(self, *cols):
        '''Add all columns to the tree'''

        self['columns'] = cols
        for col in cols:
            self.column(col, anchor=tk.W)
            self.heading(col, text=col, anchor=tk.W)

    def set_widths(self, *widths):
        '''Set column widths'''

        i = 0
        for width in widths:
            self.column(i, minwidth=width, width=width)
            i += 1


class TrafficLight():
    '''Tk based traffic light'''

    def __init__(self, parent, row: int, column: int):
        self.colour = 'red'
        self.canvas = tk.Canvas(parent, width=20, height=20)
        self.canvas.grid(row=row, column=column, padx=PAD_X, pady=PAD_Y)
        self.light = self.canvas.create_oval(5, 5, 20, 20, fill=self.colour)
        self._fill = None
        self._flash = False
        self._timer = None

    def gray(self):
        self.canvas.itemconfigure(self.light, fill='darkgray')

    def green(self):
        self.canvas.itemconfigure(self.light, fill='green')

    def red(self):
        self.canvas.itemconfigure(self.light, fill='red')

    async def _flash_callback(self):
        if self._flash:
            self._flash = False
            self.canvas.itemconfigure(self.light, fill=self._fill)
        else:
            self._flash = True
            self.canvas.itemconfigure(self.light, fill='darkgray')

    async def flash(self, fill: str = 'green', start: bool = None, stop: bool = None):
        '''Start or stop flashing'''
        if start and not self._timer:
            self._fill = fill
            self._timer = Timer(0.5, self._flash_callback, repeat=True)
        if stop and self._timer:
            self._timer.cancel()


class Timer:
    '''Async Timer with optional repeat'''

    def __init__(self, timeout, callback, repeat: bool = False):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._repeat = repeat

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()
        if self._repeat:
            self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        '''Cancel task'''
        self._task.cancel()

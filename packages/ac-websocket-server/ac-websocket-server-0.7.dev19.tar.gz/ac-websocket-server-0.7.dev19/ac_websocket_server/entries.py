'''Assetto Corsa entry_list.ini helper Class to re-order and re-write'''

import configparser
import copy
import json
from enum import Enum, auto
import logging
import random
import sys
from typing import Any, Dict, List


from ac_websocket_server.objects import EntryInfo
from ac_websocket_server.error import WebsocketsServerError

EXTRA_DEBUG = True


class EntryListIterationMethod(Enum):
    '''Iteration method to rewrite file in various manners.'''
    ORIGINAL = auto()
    FINISHING = auto()
    REVERSE = auto()
    RANDOM = auto()


class EntryList:
    '''A collection of individual Entry for the entry_list.ini file'''

    def __init__(self, file_name: str = None, entries: Dict[int, EntryInfo] = None) -> None:
        '''
        Create a new EntryList with optional input file and pre-populated entries.
        '''

        self.__logger = logging.getLogger('ac-ws.entries')

        self.file_name = file_name

        if entries:
            self.entries = entries
        else:
            self.entries = {}

        self.entries_by_entries = list()

        if file_name and not entries:
            self.parse_entries_file()

        self.results = {}

        self.results_by_entries = list()
        self.results_by_missing = list()
        self.results_by_finish = list()

        self.results_by_order = list()

        self.iteration_order = EntryListIterationMethod.ORIGINAL

    def parse_entries_file(self):
        '''Parse the original entries file.'''

        if self.file_name:

            try:
                config = configparser.ConfigParser()
                config.read(self.file_name)

                for car_id in config.sections():

                    car = config[car_id]

                    idx = int(car_id.replace('CAR_', ''))

                    self.entries[idx] = \
                        EntryInfo(car_id=car_id,
                                  model=car.get('MODEL', ''),
                                  skin=car.get('SKIN', ''),
                                  spectator_mode=car.get('SPECTATOR_MODE', ''),
                                  drivername=car.get('DRIVERNAME', ''),
                                  team=car.get('TEAM', ''),
                                  guid=car.get('GUID', ''),
                                  ballast=car.get('BALLAST', ''),
                                  restrictor=car.get('RESTRICTOR', '')
                                  )

                    self.entries_by_entries.append(idx)

            except configparser.Error as error:
                raise WebsocketsServerError(error) from error

    def parse_result_file(self, result_file: str, track: str = None):
        '''Parse AC race results file'''
        # pylint: disable=invalid-name, logging-fstring-interpolation

        try:
            with open(result_file, 'r', encoding='UTF-8') as f:
                data = json.load(f)
        except OSError as error:
            self.__logger.error(f'Unable to read input file: {result_file}')
            raise OSError from error

        if track and track != data["TrackName"]:
            raise WebsocketsServerError(
                f'TrackName from {result_file} does not match {track}')

        self.results_by_finish = list()

        cars = data["Cars"]

        for car in cars:

            car_id = car['CarId']

            self.results[car_id] = \
                EntryInfo(car_id=car_id,
                          model=car['Model'],
                          skin=car['Skin'],
                          spectator_mode=self.entries[car_id].spectator_mode,
                          drivername=car['Driver']['Name'],
                          team=car['Driver']['Team'],
                          guid=car['Driver']['Guid'],
                          ballast=car['BallastKG'],
                          restrictor=car['Restrictor']
                          )

            self.results_by_entries.append(car_id)

        results = data["Result"]

        for result in results:

            car_id = result['CarId']
            total_time = result['TotalTime']

            try:
                if total_time > 0:
                    self.results_by_finish.append(car_id)
                else:
                    self.results_by_missing.append(car_id)
            except KeyError as error:
                msg = f'Entry for {error} missing from entry.ini'
                self.__logger.error(msg=msg)
                raise WebsocketsServerError(msg) from error

        all_entries_in_results = set(
            self.results_by_finish + self.results_by_missing)
        all_entries_in_entries = set(self.entries_by_entries)
        set_of_missing_entries = all_entries_in_entries.difference(
            all_entries_in_results)

        for missing in set_of_missing_entries:
            self.results[missing] = copy.deepcopy(self.entries[missing])
            self.results_by_missing.append(missing)

        if EXTRA_DEBUG:
            print(f'results_by_finish = {self.results_by_finish}')
            print(f'results_by_missing = {self.results_by_missing}')

    def __repr__(self):
        '''Create a string representation based on IterationMethod'''

        self.__set_output_order()

        entries = ""

        position = 0
        for car_id in self.results_by_order:
            self.results[car_id].new_id = position
            entries += str(self.results[car_id])
            position += 1

        return entries

    def __set_output_order(self):
        '''Set the output order based on iteration method'''

        if self.iteration_order == EntryListIterationMethod.ORIGINAL:
            self.results_by_order = self.entries_by_entries

        if self.iteration_order == EntryListIterationMethod.FINISHING:
            self.results_by_order = self.results_by_finish + self.results_by_missing

        if self.iteration_order == EntryListIterationMethod.REVERSE:
            results_by_reversed = copy.deepcopy(self.results_by_finish)
            results_by_reversed.reverse()
            self.results_by_order = results_by_reversed + self.results_by_missing

        if self.iteration_order == EntryListIterationMethod.RANDOM:
            raise ValueError('Not Implemented')

    def set_original_order(self):
        '''Set iteration to original cars order from entry list'''
        self.iteration_order = EntryListIterationMethod.ORIGINAL

    def set_standard_order(self):
        '''Set iteration to finishing order form last race'''
        self.iteration_order = EntryListIterationMethod.FINISHING

    def set_random_order(self):
        '''Set iteration to random'''
        self.iteration_order = EntryListIterationMethod.RANDOM

    def set_reversed_order(self):
        '''Set iteration to reversed grid from last race'''
        self.iteration_order = EntryListIterationMethod.REVERSE

    def show_entries(self) -> str:
        '''Returns a dictionary representation of all cars from entry_list.ini'''

        original_iteration_method = self.iteration_order
        self.iteration_order = EntryListIterationMethod.ORIGINAL

        self.__set_output_order()

        entries = {}

        position = 1
        for car_id in self.results_by_order:
            entry = self.entries[car_id]
            entry.new_id = position
            if entry.drivername is not None:
                driver_details = f'{entry.drivername} ({entry.guid})'
            else:
                driver_details = f'{entry.drivername}'
            entries[str(position)] = f'{entry.model}{driver_details}'
            position += 1

        self.iteration_order = original_iteration_method

        return entries

    def show_grid(self) -> Dict[str, Any]:
        '''Returns a dictionary representation of the grid by player'''

        self.__set_output_order()

        entries = {}

        position = 1
        for car_id in self.results_by_order:
            if car_id not in self.results_by_missing:
                if not self.results:
                    entries[position] = self.entries[car_id].drivername
                else:
                    entries[position] = self.results[car_id].drivername
                position += 1

        return entries

    def write(self, output_file):
        '''Write updated entry list to output_file'''
        # pylint: disable=invalid-name, logging-fstring-interpolation

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(self))
                f.close()
        except OSError as err:
            self.__logger.error(f'Unable to write output file: {output_file}')
            raise OSError from err

        if EXTRA_DEBUG:
            print('entry_list.ini:')
            print(str(self))

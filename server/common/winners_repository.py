from multiprocessing import Semaphore
import logging

from .utils import *

class WinnersRepository:
    def __init__(self):
        self._winners_semaphore = Semaphore(1)
        self._processing_winners = False
        pass

    def save_winners(self, winners: 'list[Contestant]'):
        logging.info("Save winners")
        logging.debug("Save {} winners".format(len(winners)))
        if winners:
            self._winners_semaphore.acquire()
            self._processing_winners = True
            persist_winners(winners)
            self._winners_semaphore.release()
            self._processing_winners = False

    def get_all_winners(self) -> 'list[Contestant]':
        logging.info("Get all winners")
        self._winners_semaphore.acquire()
        self._processing_winners = True
        file = open(STORAGE, 'r')
        lines = file.readlines()
        contestants = list()
        for line in lines:
            contestants.append(self.__get_contestant_from_line(line))
        self._winners_semaphore.release()
        self._processing_winners = False
        return contestants

    def __get_contestant_from_line(self, line: str) -> Contestant:
        contestant_data = line.split(CONTESTANT_DATA_SEPARATOR)
        first_name = self.__get_contestant_data_from_line(contestant_data[0])
        last_name = self.__get_contestant_data_from_line(contestant_data[1])
        document = self.__get_contestant_data_from_line(contestant_data[2])
        birth_date = self.__get_contestant_data_from_line(contestant_data[3])
        agency = self.__get_contestant_data_from_line(contestant_data[4])
        return Contestant(first_name, last_name, document, birth_date, agency)

    def __get_contestant_data_from_line(self, contestant_data: str) -> str:
        return contestant_data.split(":")[1].strip()

    def processing_winners(self) -> bool:
        return self._processing_winners
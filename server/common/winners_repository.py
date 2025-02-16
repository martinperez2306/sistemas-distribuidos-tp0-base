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
            persist_winners(winners)
            self._winners_semaphore.release()

    def get_all_winners(self) -> 'list[Contestant]':
        logging.info("Get all winners")
        self._winners_semaphore.acquire()
        file = open(STORAGE, 'r')
        lines = file.readlines()
        contestants = list()
        for line in lines:
            contestants.append(self.__get_contestant_from_line(line))
        self._winners_semaphore.release()
        return contestants

    def __get_contestant_from_line(self, line: str) -> Contestant:
        contestant_data = line.split(STORAGE_DATA_SEPARATOR)
        full_name = self.__get_contestant_data_from_line(contestant_data[0])
        last_name = ""
        document = self.__get_contestant_data_from_line(contestant_data[1])
        birth_date = self.__get_contestant_data_from_line(contestant_data[2])
        return Contestant(full_name, last_name, document, birth_date)

    def __get_contestant_data_from_line(self, contestant_data: str) -> str:
        return contestant_data.split(":")[1].strip()

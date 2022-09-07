from multiprocessing import Semaphore
import logging

from .utils import Contestant
from .utils import *
from datetime import datetime

BATCH_SEPARATOR = "&"

PLAYER_DATA_SIZE = 4

class WinnerService:
    def __init__(self):
        self._winners_semaphore = Semaphore(1)
        pass

    def get_winners_response(self, message: str):
        logging.info("Get winners response")
        logging.debug("Get winners response. MSG: {}".format(message))
        contestants = self.__get_contestants(message)
        winners = self.__get_winners(contestants)
        logging.debug("Get winners response. Winners: {}".format(winners))
        self.__save_winners(winners)
        response = self.__get_winners_string(winners)
        logging.info("Get winners response. Response: {}".format(response))
        return response

    def __get_contestants(self, message: str):
        logging.info("Get Contestants.".format(message))
        logging.debug("Get Contestants. MSG: {}".format(message))
        player_list = self.__parse_batch_message(message)
        contestant_list = []
        for player_msg in player_list:
            contestant = self.__parse_contestant_message(player_msg)
            if (contestant):
                contestant_list.append(contestant)
        return contestant_list

    def __parse_batch_message(self, batch_message: str):
        parsed = batch_message.split(BATCH_SEPARATOR)
        return parsed


    def __parse_contestant_message(self, contestant_message: str):
        split = contestant_message.split(CONTESTANT_SEPARATOR)
        if (len(split) == PLAYER_DATA_SIZE):
            first_name = split[0]
            last_name = split[1]
            document = split[2]
            birth_date = split[3]
            try:
                _ = datetime.strptime(birth_date, CONTESTANT_BIRTHDATE_FORMAT)
                return Contestant(first_name, last_name, document, birth_date)
            except ValueError:
                logging.info("The string is not a date with format " + CONTESTANT_BIRTHDATE_FORMAT)
        return None

    def __get_winners(self, contestants: 'list[Contestant]'):
        logging.info("Get winners.")
        winner_list = []
        for contestant in contestants:
            is_player_winner = False
            if (contestant):
                is_player_winner = is_winner(contestant)
            if(is_player_winner):
                winner_list.append(contestant)
        return winner_list

    def __save_winners(self, winners: 'list[Contestant]'):
        logging.info("Save winners")
        logging.debug("Save {} winners".format(len(winners)))
        if winners:
            self._winners_semaphore.acquire()
            persist_winners(winners)
            self._winners_semaphore.release()

    def __get_winners_string(self, winners: 'list[Contestant]'):
        string = ""
        for winner in winners:
            string += winner.to_string()
            string += BATCH_SEPARATOR
        if not winners:
            string = "empty"
        return string


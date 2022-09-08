from multiprocessing import Semaphore
import logging


from .winners_repository import WinnersRepository
from .utils import *
from datetime import datetime

BATCH_SEPARATOR = "&"

PLAYER_DATA_SIZE = 4

AGENCIES = 5

class WinnersService:
    def __init__(self):
        self._winners_repository = WinnersRepository()
        pass

    def get_winners_response(self, client: str, players_msg: str) -> str:
        logging.info("Get winners response")
        logging.debug("Get winners response. Client: {}. Players Message: {}".format(client, players_msg))
        contestants = self.__get_contestants_from_message(client, players_msg)
        winners = self.__get_winners(contestants)
        logging.debug("Get winners response. Winners: {}".format(winners))
        self._winners_repository.save_winners(winners)
        response = self.__get_winners_string(winners)
        logging.info("Get winners response. Response: {}".format(response))
        return response

    def get_all_winners_response(self, client: str) -> str:
        logging.info("Get all winners response")
        logging.debug("Get all winners response. Client: {}".format(client))
        all_winners = self._winners_repository.get_all_winners()
        response = self.__get_winners_string(all_winners)
        logging.info("Get all winners response. Response: {}".format(response))
        return response

    def __get_contestants_from_message(self, client: str, players_msg: str) -> 'list[Contestant]':
        logging.info("Get Contestants")
        logging.debug("Get Contestants. Client: {}. Players Message: {}".format(client, players_msg))
        player_list = self.__parse_batch_message(players_msg)
        contestant_list = []
        for player_msg in player_list:
            contestant = self.__parse_contestant_message(client, player_msg)
            if (contestant):
                contestant_list.append(contestant)
        return contestant_list

    def __parse_batch_message(self, batch_message: str) -> 'list[str]':
        return batch_message.split(BATCH_SEPARATOR)


    def __parse_contestant_message(self, client, player_message: str):
        split = player_message.split(CONTESTANT_SEPARATOR)
        if (len(split) == PLAYER_DATA_SIZE):
            first_name = split[0]
            last_name = split[1]
            document = split[2]
            birth_date = split[3]
            try:
                _ = datetime.strptime(birth_date, CONTESTANT_BIRTHDATE_FORMAT)
                return Contestant(first_name, last_name, document, birth_date, client)
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

    def __get_winners_string(self, winners: 'list[Contestant]') -> str:
        string = ""
        for winner in winners:
            string += winner.to_string()
            string += BATCH_SEPARATOR
        if not winners:
            string = "empty"
        return string


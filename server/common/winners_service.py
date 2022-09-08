import datetime
import logging

from .winners_track import WinnersTrack
from .winners_repository import WinnersRepository
from .utils import *

ENTITY_SEPARATOR = "&"

PLAYER_DATA_SIZE = 4

class WinnersService:
    def __init__(self):
        self._winners_repository = WinnersRepository()
        self._winners_track = WinnersTrack()
        pass

    def get_winners_response(self, client: str, players_msg: str) -> str:
        logging.info("Get winners response")
        logging.debug("Get winners response. Client: {}. Players Message: {}".format(client, players_msg))
        self._winners_track.track_init_process(client)
        contestants = self.__get_contestants_from_message(client, players_msg)
        winners = self.__get_winners(contestants)
        logging.debug("Get winners response. Winners: {}".format(winners))
        self._winners_repository.save_winners(winners)
        response = self.__get_winners_string(winners)
        self._winners_track.track_finish_process(client)
        logging.info("Get winners response. Response: {}".format(response))
        return response

    def get_agencies_winners_response(self, client: str) -> str:
        logging.info("Get winners by agency response")
        logging.debug("Get winners by agency response. Client: {}".format(client))
        response = "PROCESS_PENDING&"
        processing_pending_count = self._winners_track.get_pending_process_count()
        if (processing_pending_count == 0):
            all_winners = self._winners_repository.get_all_winners()
            agencies = list()
            logging.debug("Max Clients Tracked: {}".format(self._winners_track.get_max_clients_tracked()))
            for agency_it in range(self._winners_track.get_max_clients_tracked()):
                agency_id = str(agency_it + 1)
                agency_winners = list(filter(lambda w: w.agency == agency_id, all_winners))
                agencies.append(Agency(agency_id, agency_winners))
            response = "PROCESS_FINISH&" + self.__get_agencies_string(agencies)
        else:
            response += str(processing_pending_count)
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
        return batch_message.split(ENTITY_SEPARATOR)


    def __parse_contestant_message(self, client, player_message: str):
        split = player_message.split(MODEL_DATA_SEPARATOR)
        if (len(split) == PLAYER_DATA_SIZE):
            first_name = split[0]
            last_name = split[1]
            document = split[2]
            birth_date = split[3]
            try:
                _ = datetime.datetime.strptime(birth_date, CONTESTANT_BIRTHDATE_FORMAT)
                return Contestant(first_name, last_name, document, birth_date, client)
            except ValueError:
                logging.info("The string is not a date with format " + CONTESTANT_BIRTHDATE_FORMAT)
        return None

    def __get_winners(self, contestants: 'list[Contestant]'):
        logging.info("Get winners")
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
            string += ENTITY_SEPARATOR
        string = string[:-1]
        if not winners:
            string = "empty"
        return string

    def __get_agencies_string(self, agencies: 'list[Agency]') -> str:
        string = ""
        for agency in agencies:
            string += agency.to_string()
            string += ENTITY_SEPARATOR
        string = string[:-1]
        return string


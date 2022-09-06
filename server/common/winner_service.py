import logging

from .utils import Contestant
from .utils import is_winner
from datetime import datetime

CONTESTANT_SEPARATOR = "_"
BATCH_SEPARATOR = "\n"

PLAYER_DATA_SIZE = 4

class WinnerService:
    def __init__(self):
        pass

    def get_winners_response(self, msg):
        logging.info("Get winners response.".format(msg))
        logging.debug("Get winners response. MSG: {}".format(msg))
        winners = self.get_winners(msg)
        logging.debug("Get winners response. Winners: {}".format(winners))
        response = ""
        for winner in winners:
            response += winner
            response += BATCH_SEPARATOR
        if not winners:
            response = "empty"
        logging.info("Get winners response. Response: {}".format(response))
        return response

    def get_winners(self, msg):
        logging.info("Get winners.".format(msg))
        logging.debug("Get winners. MSG: {}".format(msg))
        player_list = self.parse_batch_message(msg)
        winner_list = []
        for player_msg in player_list:
            is_player_winner = False
            contestant = self.parse_contestant_message(player_msg)
            if (contestant):
                is_player_winner = is_winner(contestant)
            if(is_player_winner):
                winner_list.append(player_msg)
        logging.info("Get winners. Winner List: {}".format(winner_list))
        return winner_list

    def parse_contestant_message(self, msg):
        format_yyyymmdd = "%Y-%m-%d"
        split = msg.split(CONTESTANT_SEPARATOR)
        if (len(split) == PLAYER_DATA_SIZE):
            first_name = split[0]
            last_name = split[1]
            document = split[2]
            birth_date = split[3]
            try:
                date = datetime.strptime(birth_date, format_yyyymmdd)
                return Contestant(first_name, last_name, document, birth_date)
            except ValueError:
                logging.info("The string is not a date with format " + format_yyyymmdd)
        return None

    def parse_batch_message(self, batch_msg):
        parsed = batch_msg.split(BATCH_SEPARATOR)
        return parsed

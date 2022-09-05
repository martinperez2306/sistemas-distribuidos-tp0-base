import logging

from .utils import Contestant
from .utils import is_winner

CONTESTANT_SEPARATOR = "_"
BATCH_SEPARATOR = "\n"

class WinnerService:
    def __init__(self):
        pass

    def get_winners_response(self, msg):
        logging.info("Get winners response. MSG: {}".format(msg))
        winners = self.get_winners(msg)
        logging.debug("Get winners response. Winners: {}".format(winners))
        response = ""
        for winner in winners:
            response += winner
            response += BATCH_SEPARATOR
        logging.info("Get winners response. Response: {}".format(response))
        if not winners:
            response = "empty"
        return response

    def get_winners(self, msg):
        logging.info("Get winners. MSG: {}".format(msg))
        player_list = self.parse_batch_message(msg)
        winner_list = []
        for player_msg in player_list:
            is_player_winner = is_winner(self.parse_contestant_message(player_msg))
            if(is_player_winner):
                winner_list.append(player_msg)
        logging.info("Get winners response. Winner List: {}".format(winner_list))
        return winner_list

    def parse_contestant_message(self, msg):
        split = msg.split(CONTESTANT_SEPARATOR)
        first_name = split[0]
        last_name = split[1]
        document = split[2]
        birth_date = split[3]
        return Contestant(first_name, last_name, document, birth_date)

    def parse_batch_message(self, batch_msg):
        logging.info("Get winners. MSG: {}".format(batch_msg))
        parsed = batch_msg.split(BATCH_SEPARATOR)
        logging.info("Get winners. MSG: {}".format(parsed))
        return parsed

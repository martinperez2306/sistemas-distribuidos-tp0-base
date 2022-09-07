import re
import logging
from .winners_service import WinnerService

REQUEST_ID_REGEX=r'REQUEST_ID\[(.*?)\]'
REQUEST_BODY_REGEX=r'REQUEST_BODY\[(.*?)\]'

GET_WINNERS = "GET_WINNERS"
GET_ALL_WINNERS = "GET_ALL_WINNERS"

class WinnersController:
    def __init__(self):
        self._winners_service = WinnerService()
        pass

    def handle_request(self, request: str) -> str:
        logging.info("Handling client request {}".format(request))
        request_parsed = self.__parse_request(request)
        if (request_parsed[0] == GET_WINNERS):
            return self.__get_winners(request_parsed[1])
        elif (request_parsed[0] == GET_ALL_WINNERS):
            return self.__get_all_winners(request_parsed[1])
        else:
            return None

    def __parse_request(self, request: str):
        request_id = re.search(REQUEST_ID_REGEX,request).group(1)
        request_body = re.search(REQUEST_BODY_REGEX,request).group(1)
        return request_id, request_body

    def __get_winners(self, body: str):
        return self._winners_service.get_winners_response(body)

    def __get_all_winners(self, body: str):
        pass
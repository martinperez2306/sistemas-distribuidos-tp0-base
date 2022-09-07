import re
import logging
from .winners_service import WinnerService

REQUEST_CLIENT_REGEX = r'REQUEST_CLI\[(.*?)\]'
REQUEST_NAME_REGEX=r'REQUEST_NAME\[(.*?)\]'
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
        if (request_parsed[1] == GET_WINNERS):
            return self.__get_winners(request_parsed[2])
        elif (request_parsed[1] == GET_ALL_WINNERS):
            return self.__get_all_winners(request_parsed[2])
        else:
            return None

    def __parse_request(self, request: str):
        request_cli = re.search(REQUEST_CLIENT_REGEX,request).group(1)
        request_id = re.search(REQUEST_NAME_REGEX,request).group(1)
        request_body = re.search(REQUEST_BODY_REGEX,request).group(1)
        return request_cli, request_id, request_body

    def __get_winners(self, body: str):
        return self._winners_service.get_winners_response(body)

    def __get_all_winners(self, body: str):
        pass
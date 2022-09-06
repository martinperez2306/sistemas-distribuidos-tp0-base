import socket
import logging

from .winner_service import WinnerService

PREPARE_MSG_SIZE = 1024
RESPONSE_MSG_SIZE = 1
CLOSE_CONN_SIZE = 2

RESPONSE_MSG_CODE = "0"
CLOSE_CONN_CODE = "-1"

BUFF_SIZE = 4096

class Communicator:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self._winner_service = WinnerService()

    def handle_communication(self):
        self._client_socket = self.__accept_new_connection()
        self.__handle_client_connection()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        try:
            c, addr = self._server_socket.accept()
            logging.info('Got connection from {}'.format(addr))
            return c
        except OSError as error:
            logging.info("Error while accept connection in server socket {}. Error: {}".format(self._server_socket, error))
            self._server_socket.close()

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and respond to it.

        Closes the socket when client request the end of communication

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            if(self._client_socket is not None):
                msg_bytes = self.__receive(PREPARE_MSG_SIZE)
                self.__respond(msg_bytes.decode('utf-8'), None)
        except ValueError as error:
            logging.info("Error while reading client message {}. Error: {}".format(self._client_socket, error))
            self.end_communication()
        except OSError as error:
            logging.info("Error while reading client socket {}. Error: {}".format(self._client_socket, error))
            self.end_communication()
        finally:
            self.end_communication()

    def __respond(self, request, response):
        try:
            int(request)
            req_is_number = True
        except ValueError:
            req_is_number = False
            
        if (req_is_number):
            request_size = int(request)
            if (request == CLOSE_CONN_CODE):
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Its time to close connection'
                        .format(self._client_socket.getpeername(), request_size))
                self.__respond_and_continue(request, response)
            elif (request == RESPONSE_MSG_CODE):
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Im ok to response data.'
                        .format(self._client_socket.getpeername(), request_size))
                logging.debug(
                            'Send winners to connection {}. Winners: {}'
                            .format(self._client_socket.getpeername(), response))
                self.__respond_and_wait(request, response, CLOSE_CONN_SIZE)
            else:
                logging.info(
                        'Message Size received from connection {}. Request Size: {}. Im ok to receive data.'
                        .format(self._client_socket.getpeername(), request_size))
                self.__respond_and_wait(request, response, request_size)
                
        else:
            if not request:
                return
            logging.info(
                        'Data received from connection {}.'
                        .format(self._client_socket.getpeername()))
            logging.debug(
                        'Data received from connection {}. Data: {}'
                        .format(self._client_socket.getpeername(), request))
            winners_msg = self._winner_service.get_winners_response(request)
            logging.info(
                        'Send recv ok to client {}. Recived: {}'
                        .format(self._client_socket.getpeername(), len(request)))
            self.__respond_and_wait(len(request), winners_msg, RESPONSE_MSG_SIZE)
            
    def __respond_and_wait(self, request, response, expected_response_size):
        """
            Responde with a message and waits for other response.
            If request is RESPONSE_MSG_CODE send the response.
            Else send the request.
        """
        msg = request
        if(request == RESPONSE_MSG_CODE):
            msg = response
        logging.info('Respond to client {} with {} and wait.'
                    .format(self._client_socket.getpeername(), msg))
        self.__send(msg)

        msg_bytes = self.__receive(expected_response_size)
        response_msg = msg_bytes.decode('utf-8')
        self.__respond(response_msg, response)

    def __respond_and_continue(self, request, response):
        """
            Responde with a message and continue.
            If request is RESPONSE_MSG_CODE send the response.
            Else send the request.
        """ 
        msg = request
        if(request == RESPONSE_MSG_CODE):
            msg = response
        logging.info('Respond to client {} with {} and continue.'
                    .format(self._client_socket.getpeername(), msg))
        self.__send(msg)

    def __receive(self, buffsize):
        """
            Receive a message.
            Read client socket specific buffsize and returns the message of communication
            It wait for first data recieved and return when all data has been readed.
        """
        logging.info('Recieving by client {} data with size: {}'
                    .format(self._client_socket.getpeername(), buffsize))
        data = b''
        if(self._client_socket is not None):
            self._client_socket.setblocking(True)
            try:
                while True:
                    data += self._client_socket.recv(BUFF_SIZE)
                    self._client_socket.setblocking(False)
            except socket.error:
                pass
            logging.info('Recived data {}: {}'
                    .format(self._client_socket.getpeername(), len(data)))
            return data

    def __send(self, msg):
        """
            Send a message.
            Write client socket specific the message of communication
        """
        if(self._client_socket is not None):
            self._client_socket.sendall("{}".format(msg).encode('utf-8'))

    def end_communication(self):
        """
            Finish the communication with client.
            Release client socket resources and close it
        """
        if(self._client_socket is not None):
            self._client_socket.close()
        self._client_socket = None

    
    def turn_off(self):
        """
            Turn off Communicator.
            Release client and server resources and close it
        """
        self.end_communication()
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
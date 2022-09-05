import socket
import logging

from .winner_service import WinnerService

PREPARE_MSG_SIZE = 4

CLOSE_CONN_FLAG = 0
CLOSE_CONN_SIZE = 1

MAX_BUFF_SIZE = 1024

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
        except OSError:
            logging.info("Error while accept connection in server socket {}".format(self._server_socket))
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
                msg_size = self.__receive(PREPARE_MSG_SIZE)
                self.__respond(msg_size)
        except ValueError:
            logging.info("Error while reading client message {}".format(self._client_socket))
            self.end_communication()
        except OSError:
            logging.info("Error while reading client socket {}".format(self._client_socket))
            self.end_communication()
        finally:
            self.end_communication()

    def __respond(self, request):
        try:
            int(request)
            req_is_number = True
        except ValueError:
            req_is_number = False
            
        if (req_is_number):
            request_size = int(request)
            if (request_size == CLOSE_CONN_FLAG):
                logging.info(
                        'Message Size received from connection {}. MsgSize: {}. Its time to close connection'
                        .format(self._client_socket.getpeername(), request_size))
                self.__respond_and_continue(request)
            else:
                logging.info(
                        'Message Size received from connection {}. MsgSize: {}. Im ok to receive data.'
                        .format(self._client_socket.getpeername(), request_size))
                self.__respond_and_wait(request, request_size)
        else:
            if not request:
                return
            logging.info(
                        'Data received from connection {}. Im ready to respond using data information'
                        .format(self._client_socket.getpeername()))
            logging.debug(
                        'Data received from connection {}. Data {}'
                        .format(self._client_socket.getpeername(), request))
            winners_msg = self._winner_service.get_winners_response(request)
            logging.info(
                        'Send is winner to connection {}.'
                        .format(self._client_socket.getpeername()))
            logging.debug(
                        'Send is winner to connection {}. Winners: {}'
                        .format(self._client_socket.getpeername(), winners_msg))
            self.__respond_and_wait(winners_msg, CLOSE_CONN_SIZE)

    def __respond_and_wait(self, msg, expected_response_size):
        self.__send(msg)
        response_msg = self.__receive(expected_response_size)
        self.__respond(response_msg)

    def __respond_and_continue(self, msg): 
        self.__send(msg)

    def __receive(self, bufsize):
        """
            Receive a message.
            Read client socket specific buffsize and returns the message of communication
        """
        if(self._client_socket is not None):
            if(bufsize < MAX_BUFF_SIZE):
                return self._client_socket.recv(bufsize).rstrip().decode('utf-8')
            else:
                data = self._client_socket.recv(MAX_BUFF_SIZE).rstrip().decode('utf-8')
                data += self.__receive(bufsize - MAX_BUFF_SIZE)

    def __send(self, msg):
        """
            Send a message.
            Write client socket specific the message of communication
        """
        if(self._client_socket is not None):
            self._client_socket.send("{}".format(msg).encode('utf-8'))

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
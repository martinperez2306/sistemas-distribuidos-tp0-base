from multiprocessing import Semaphore
import socket
import logging
import threading

from .winners_controller import WinnersController

PREPARE_MSG_SIZE = 12
RESPONSE_MSG_SIZE = 13
CLOSE_CONN_SIZE = 13

RESPONSE_MSG_CODE = "0000000000000"
SEND_RESPONSE_MSG_CODE = "0000000000001"
CLOSE_CONN_CODE = "9999999999999"

BUFF_SIZE = 4096

ENCODING = "utf-8"

class Communicator:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._winner_controller = WinnersController()
        self._client_sockets_semaphore = Semaphore(1)
        self._client_sockets = list()

    def handle_communication(self):
        client_socket = self.__accept_new_connection()
        client_connection_thread = threading.Thread(target=self.__handle_client_connection, args=(client_socket,))
        client_connection_thread.setDaemon(True)
        client_connection_thread.start()

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

    def __handle_client_connection(self, client_socket: socket):
        """
        Read message from a specific client socket and respond to it.

        Closes the socket when client request the end of communication

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        if(client_socket is not None):
            logging.info("Handling client connection {}".format(client_socket))
            try:
                self.__init_connection(client_socket)
                request = self.__get_request(client_socket)
                response = self.__handle_request(client_socket, request)
                close_connection_request = self.__send_response(client_socket, response)
                self.__confirm_close_connection(client_socket, close_connection_request)
            except ValueError as error:
                logging.info("Error while reading client message {}. Error: {}".format(client_socket, error))
                self.__end_connection(client_socket)
            except OSError as error:
                logging.info("Error while reading client socket {}. Error: {}".format(client_socket, error))
                self.__end_connection(client_socket)
            finally:
                self.__end_connection(client_socket)

    def __init_connection(self, client_socket: socket):
        if(client_socket is not None):
            logging.info('Init Connection: {}'.format(client_socket.getpeername()))
            self._client_sockets_semaphore.acquire()
            self._client_sockets.append(client_socket)
            self._client_sockets_semaphore.release()

    def __get_request(self, client_socket: socket):
        if(client_socket is not None):
            logging.info('Get request from connection {}'.format(client_socket.getpeername()))
            request_prepare = self.__receive(client_socket, PREPARE_MSG_SIZE)
            request_msg: str = request_prepare.decode(ENCODING)
            try:
                request_size = int(request_msg)
                logging.info('Message Size received from connection {}. Request Size: {}. Im ok to receive data.'
                            .format(client_socket.getpeername(), request_size))
                return self.__respond_and_wait(client_socket, request_prepare, request_size)
            except ValueError:
                logging.info('Message received from connection {} is not prepare message {}.'
                            .format(client_socket.getpeername(), request_msg))

    def __handle_request(self, client_socket: socket, request: bytes):
        request_msg: str = request.decode(ENCODING)
        logging.info('Data received from connection {}.'.format(client_socket.getpeername()))
        logging.debug('Data received from connection {}. Data: {}'.format(client_socket.getpeername(), request_msg))
        recived_len = str(len(request))
        logging.info('Send recv ok to connection {}. Recived: {}'.format(client_socket.getpeername(), recived_len))
        winners_msg = self._winner_controller.handle_request(request_msg)
        self.__respond_and_wait(client_socket, request, RESPONSE_MSG_SIZE)
        return winners_msg.encode(ENCODING)

    def __send_response (self, client_socket: socket, response: bytes):
        winners_size = len(response)
        logging.info('Telling connection {} response size'.format(client_socket.getpeername()))
        logging.debug('Send winners size to connection {}. Winners Size: {}'.format(client_socket.getpeername(), winners_size))
        winners_size_response = str(winners_size).zfill(RESPONSE_MSG_SIZE).encode(ENCODING)
        client_confirmation = self.__respond_and_wait(client_socket, winners_size_response, RESPONSE_MSG_SIZE)
        client_confirmation_msg = client_confirmation.decode(ENCODING)
        logging.info('Confirmation {}. Im ok to response data to connection {}'.format(client_confirmation_msg, client_socket.getpeername()))
        logging.debug('Send winners to connection {}. Winners: {}'.format(client_socket.getpeername(), response.decode(ENCODING)))
        return self.__respond_and_wait(client_socket, response, CLOSE_CONN_SIZE)

    def __confirm_close_connection(self, client_socket: socket, request: bytes):
        logging.info('Its time to close connection {}'
                .format(client_socket.getpeername()))
        self.__respond_and_continue(client_socket, request)
            
    def __respond_and_wait(self, client_socket: socket, response: bytes, expected_response_size: int):
        """
            Responde with a message and waits for other response.
            Return the new response
        """
        logging.info('Respond to connection {} with {} and wait.'.format(client_socket.getpeername(), response.decode(ENCODING)))
        self.__send(client_socket, response)
        return self.__receive(client_socket, expected_response_size)

    def __respond_and_continue(self, client_socket: socket, response: bytes):
        """
            Responde with a message and continue.
        """ 
        logging.info('Respond to connection {} with {} and continue.'.format(client_socket.getpeername(), response.decode(ENCODING)))
        self.__send(client_socket, response)

    def __receive(self, client_socket: socket, buffsize: int):
        """
            Receive a message.
            Read client socket specific buffsize and returns the message of communication
            It wait for first data recieved and return when all data has been readed.
        """
        logging.info('Recieving by connection {} data with size: {}'.format(client_socket.getpeername(), buffsize))
        data = b''
        if(client_socket is not None):
            client_socket.setblocking(True)
            while len(data) < buffsize:
                try:
                    data += client_socket.recv(BUFF_SIZE)
                    client_socket.setblocking(False)
                except socket.error:
                    pass
            logging.info('Recived len data {}: {}'.format(client_socket.getpeername(), len(data)))
            logging.debug('Recived data {}: {}'.format(client_socket.getpeername(), data.decode(ENCODING)))
            return data

    def __send(self, client_socket, msg: bytes):
        """
            Send a message.
            Write client socket specific the message of communication
        """
        logging.info('Sending len data: {}'.format(len(msg)))
        if(client_socket is not None):
            client_socket.setblocking(True)
            client_socket.sendall(msg)

    def __end_connection(self, client_socket):
        """
            Finish the connection with client.
            Release client socket resources and close it
        """
        if(client_socket is not None):
            logging.info('End connection: {}'.format(client_socket.getpeername()))
            self._client_sockets_semaphore.acquire()
            self._client_sockets = list(filter(lambda c: c.getpeername()[0] != client_socket.getpeername()[0] and c.getpeername()[1] != client_socket.getpeername()[1], self._client_sockets))
            client_socket.close()
            self._client_sockets_semaphore.release()

    def turn_off(self):
        """
            Turn off Communicator.
            Release clients and server resources and close it
        """
        for client_socket in self._client_sockets:
            self.__end_connection(client_socket)
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
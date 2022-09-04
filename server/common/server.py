import socket
import logging
import signal

from .utils import Contestant
from .utils import is_winner


class Server:

    def __init__(self, port, listen_backlog):
        self.running = True
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        # Set signals to catch
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # graceful shutdown the server
    def exit_gracefully(self, *args):
        logging.info("Proceed to shutdown server gracefully")
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self.running = False

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self.running:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

        logging.info("Server stop running")

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            if(client_sock is not None):
                msg_size = client_sock.recv(4).rstrip().decode('utf-8')
                logging.info(
                    'Message Size received from connection {}. MsgSize: {}'
                    .format(client_sock.getpeername(), msg_size))
                client_sock.send("{}".format(msg_size).encode('utf-8'))
                msg = client_sock.recv(int(msg_size)).rstrip().decode('utf-8')
                logging.info(
                    'Message received from connection {}. Msg: {}'
                    .format(client_sock.getpeername(), msg))
                first_name, last_name, document, birth_date = self.__parse_client_message(msg)
                #contestant = Contestant(first_name, last_name, document, birth_date)
                is_contstant_winner = is_winner(True)
                logging.info(
                    'Send is winner to connection {}. Is Winner: {}'
                    .format(client_sock.getpeername(), is_contstant_winner))
                client_sock.send("{}".format(is_contstant_winner).encode('utf-8'))
        except ValueError:
            logging.info("Error while reading client message {}".format(client_sock))
        except OSError:
            logging.info("Error while reading client socket {}".format(client_sock))
        finally:
            if(client_sock is not None):
                client_sock.close()

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

    def __parse_client_message(self, msg):
        split = msg.split("_")
        first_name = split[0]
        last_name = split[1]
        document = split[2]
        birth_date = split[3]
        return first_name, last_name, document, birth_date

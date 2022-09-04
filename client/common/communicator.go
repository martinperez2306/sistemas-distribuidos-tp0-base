package common

import (
	"fmt"
	"net"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
)

type Communicator struct {
	conn            net.Conn
	serverAddress   string
	communicationTO time.Duration
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewCommunicator(config ClientConfig) *Communicator {
	communicator := &Communicator{
		serverAddress:   config.ServerAddress,
		communicationTO: config.CommunicationTO,
	}
	return communicator
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (communicator *Communicator) createClientSocket(client Client) error {
	conn, err := net.Dial("tcp", client.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"[CLIENT %v] Could not connect to server. Error: %v",
			client.config.ID,
			err,
		)
	}
	communicator.conn = conn
	return nil
}

func (communicator *Communicator) check_winner(clientID string, msg string) {
	msg_length := len(msg)

	data, err := communicator.send_and_wait(clientID, strconv.Itoa(msg_length), 4)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
	}

	accepted_server_size_msg, _ := strconv.Atoi(data)

	log.Infof("[CLIENT %v] Receive server data %d", clientID, accepted_server_size_msg)

	if accepted_server_size_msg == msg_length {
		log.Infof("[CLIENT %v] Im ok to send message data %d", clientID, msg)
		data, err := communicator.send_and_wait(clientID, msg, 1)
		if err != nil {
			log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		}

		log.Infof("[CLIENT %v] Message from server: %v", clientID, data)

		winner_server_msg, err := strconv.ParseBool(string(data))

		log.Infof("[CLIENT %v] Message from server %t", clientID, winner_server_msg)

		if winner_server_msg {
			log.Infof("[CLIENT %v] IM WINNER!", clientID)
		} else {
			log.Infof("[CLIENT %v] Im not winner :(", clientID)
		}

	} else {
		log.Infof("[CLIENT %v] I cant send message data %d to server", clientID, msg)
	}

	// Close connection to the server
	communicator.shutdown()
}

func (communicator *Communicator) send_and_wait(clientID string, msg string, expected_response_size int) (string, error) {
	read_buff := make([]byte, expected_response_size)
	data := make([]byte, 0)
	log.Infof("[CLIENT %v] Send message: %v and wait: %v for response with size: %d", clientID, msg, communicator.communicationTO, expected_response_size)
	fmt.Fprintf(communicator.conn, "%s", msg)

	log.Debugf("[CLIENT %v] Waiting response for message %v", clientID, msg)
	communicator.conn.SetReadDeadline(time.Now().Add(communicator.communicationTO))

	n, err := communicator.conn.Read(read_buff)

	if err != nil {
		log.Infof("[CLIENT %v] Read error: %s", clientID)
		communicator.shutdown()
		return "", err
	}

	data = append(data, read_buff[:n]...)

	log.Infof("[CLIENT %v] Message from server: %v", clientID, data)
	return string(data), nil
}

func (communicator *Communicator) shutdown() {
	communicator.conn.Close()
}

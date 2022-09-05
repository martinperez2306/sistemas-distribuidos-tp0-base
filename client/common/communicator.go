package common

import (
	"errors"
	"fmt"
	"net"
	"strconv"
	"time"

	log "github.com/sirupsen/logrus"
)

const RESPONSE_MSG = 0
const CLOSE_CONN_MSG = -1

const PREPARE_MSG_SIZE = 4
const CLOSE_MSG_SIZE = 2

// Communicator Entity
type Communicator struct {
	conn            net.Conn
	serverAddress   string
	communicationTO time.Duration
}

// NewCommunicator Initializes a new comminictor receiving the configuration
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

// Send request to server and return the response.
// Request needs a message. The response is string.
// If any error occurs then return it.
func (communicator *Communicator) request(clientID string, msg string) (string, error) {
	request, req_err := communicator.sendRequest(clientID, msg)
	if req_err != nil {
		return "", req_err
	}

	response, res_err := communicator.getResponse(clientID, request, len(request))
	if res_err != nil {
		return "", req_err
	}

	_, end_err := communicator.endCommunication(clientID)
	if end_err != nil {
		return "", end_err
	}

	return response, nil
}

func (communicator *Communicator) sendRequest(clientID string, msg string) (string, error) {
	msg_length := len(msg)

	log.Infof("[CLIENT %v] Send request: %v", clientID, msg)
	//Step 1: Tell to server the Request Length and wait for Server Confirmation

	data, err := communicator.sendAndWait(clientID, strconv.Itoa(msg_length), PREPARE_MSG_SIZE)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return "", err
	}

	accepted_server_size_msg, _ := strconv.Atoi(data)

	log.Infof("[CLIENT %v] Accepted Server Size Message %d", clientID, accepted_server_size_msg)

	//Step 2: Check Server Confirmation and send Request Message

	if accepted_server_size_msg == msg_length {
		log.Infof("[CLIENT %v] Im ok to send message data %s", clientID, msg)
		data, err := communicator.sendAndWait(clientID, msg, msg_length)

		if err != nil {
			log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
			communicator.shutdown()
			return "", err
		}

		log.Infof("[CLIENT %v] Request confirmation data %s", clientID, data)

		return data, nil

	} else {
		log.Infof("[CLIENT %v] I cant send message data %v to server", clientID, msg)
		return "", errors.New("Cant send message data to server")
	}
}

func (communicator *Communicator) getResponse(clientID string, request string, expectedResponseSize int) (string, error) {
	log.Infof("[CLIENT %v] Get Response for request: %v and expected size %d", clientID, request, expectedResponseSize)
	//Step 3: Tell to server we want Response of the Request

	data, err := communicator.sendAndWait(clientID, strconv.Itoa(RESPONSE_MSG), expectedResponseSize) //The client receives at most the same message

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return "", err
	}

	log.Infof("[CLIENT %v] Response data %s", clientID, data)

	return data, nil
}

func (communicator *Communicator) endCommunication(clientID string) (string, error) {
	//Step 4: Tell the server to end the communication. It will be notified with a message size equal to zero.

	log.Infof("[CLIENT %v] Send ends connection", clientID)
	end_connection_data, err := communicator.sendAndWait(clientID, strconv.Itoa(CLOSE_CONN_MSG), CLOSE_MSG_SIZE)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return "", err
	}

	end_communication_server_msg, _ := strconv.Atoi(end_connection_data)

	if end_communication_server_msg == CLOSE_CONN_MSG {
		log.Infof("[CLIENT %v] Close connection successfuly", clientID)
	} else {
		log.Infof("[CLIENT %v] Close connection with error: %v", clientID, err.Error())
	}

	communicator.shutdown()

	return end_connection_data, nil
}

// Send message to server and waits for a response
// If no response arrives at specefic time, throws TimeOut error
func (communicator *Communicator) sendAndWait(clientID string, msg string, expectedResponseSize int) (string, error) {
	log.Infof("[CLIENT %v] Send message: %v and wait: %v for response with size: %d", clientID, msg, communicator.communicationTO, expectedResponseSize)
	readBuff := make([]byte, expectedResponseSize)
	data := make([]byte, 0)

	fmt.Fprintf(communicator.conn, "%s", msg)

	log.Debugf("[CLIENT %v] Waiting response for message %v", clientID, msg)
	communicator.conn.SetReadDeadline(time.Now().Add(communicator.communicationTO))

	n, err := communicator.conn.Read(readBuff)

	if err != nil {
		log.Infof("[CLIENT %v] Read error: %s", clientID, err.Error())
		communicator.shutdown()
		return "", err
	}

	data = append(data, readBuff[:n]...)

	responseMsg := string(data)

	log.Infof("[CLIENT %v] Response Message from server: %v", clientID, responseMsg)
	return responseMsg, nil
}

// Ends communication with server
func (communicator *Communicator) shutdown() {
	communicator.conn.Close()
}

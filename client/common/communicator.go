package common

import (
	"fmt"
	"net"
	"time"

	log "github.com/sirupsen/logrus"
)

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
		log.Infof("[CLIENT %v] Read error: %s", clientID)
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

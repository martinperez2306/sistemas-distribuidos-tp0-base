package common

import (
	"fmt"
	"io"
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

func (communicator *Communicator) send(clientID string, msg string) {
	msg_length := len(msg)

	// Send
	fmt.Fprintf(communicator.conn, "%d", msg_length)
	read_buff := make([]byte, 4)
	n, err := communicator.conn.Read(read_buff)
	data := make([]byte, 0)
	data = append(data, read_buff[:n]...)

	if err != nil {
		log.Errorf(
			"[CLIENT %v] Error reading from socket. %v.",
			clientID,
			err,
		)
		communicator.conn.Close()
		return
	}

	log.Infof("[CLIENT %v] Message from server: %v", clientID, data)

	server_msg_int, _ := strconv.Atoi(string(data))

	log.Infof("[CLIENT %v] Message from server %d", clientID, server_msg_int)

	if server_msg_int == msg_length {
		fmt.Fprintf(communicator.conn, "%v", msg)
	}

	read_buff_2 := make([]byte, 1)
	data2 := make([]byte, 0)
loop2:
	for timeout2 := time.After(3 * time.Second); ; { //establecer TO
		select {
		case <-timeout2:
			break loop2
		default:
		}

		n2, err2 := communicator.conn.Read(read_buff_2)
		data2 = append(data2, read_buff_2[:n2]...)

		if err2 != nil {
			if err2 != io.EOF {
				log.Printf("Read error: %s", err2)
				communicator.conn.Close()
				return
			}
		} else {
			break loop2
		}

	}

	log.Infof("[CLIENT %v] Message from server: %v", clientID, data2)

	server_msg_2, err := strconv.ParseBool(string(data2))

	log.Infof("[CLIENT %v] Message from server %t", clientID, server_msg_2)

	if server_msg_2 {
		log.Infof("[CLIENT %v] IM WINNER!", clientID)
	} else {
		log.Infof("[CLIENT %v] Im not winner :(", clientID)
	}

	// Close connection to the server
	communicator.shutdown()
}

func (communicator *Communicator) shutdown() {
	communicator.conn.Close()
}

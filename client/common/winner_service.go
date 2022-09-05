package common

import (
	"bytes"
	"strconv"

	log "github.com/sirupsen/logrus"
)

const MSG_SEPARATOR string = "_"

const CLOSE_CONN_MSG = 0

const PREPARE_MSG_SIZE = 4
const CONFIRMATION_MSG_SIZE = 1

type WinnerService struct {
}

// NewPlayer Initializes a new Winner Service
func NewWinnerService() *WinnerService {
	winnerService := &WinnerService{}
	return winnerService
}

// Check if Player is a Winner sending message to server with communicator
func (winnerService *WinnerService) checkWinner(communicator *Communicator, clientID string, player Player) {
	msg := winnerService.getPlayerMsg(player)

	msg_length := len(msg)

	//Step 1: Tell to server the Player Message Length and wait for Server Confirmation

	data, err := communicator.sendAndWait(clientID, strconv.Itoa(msg_length), PREPARE_MSG_SIZE)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return
	}

	accepted_server_size_msg, _ := strconv.Atoi(data)

	log.Infof("[CLIENT %v] Accepted Server Size Message %d", clientID, accepted_server_size_msg)

	//Step 2: Check Server Confirmation and send Player Message

	if accepted_server_size_msg == msg_length {
		log.Infof("[CLIENT %v] Im ok to send message data %s", clientID, msg)
		data, err := communicator.sendAndWait(clientID, msg, CONFIRMATION_MSG_SIZE)

		if err != nil {
			log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
			communicator.shutdown()
			return
		}

		winner_server_msg, err := strconv.ParseBool(data)

		log.Infof("[CLIENT %v] Winner Server Message %t", clientID, winner_server_msg)

		if winner_server_msg {
			log.Infof("[CLIENT %v] IM WINNER!", clientID)
		} else {
			log.Infof("[CLIENT %v] Im not winner :(", clientID)
		}

	} else {
		log.Infof("[CLIENT %v] I cant send message data %v to server", clientID, msg)
	}

	//Step 3: Tell the server to end the communication. It will be notified with a message size equal to zero.

	log.Infof("[CLIENT %v] Send ends connection", clientID)
	end_connection_data, err := communicator.sendAndWait(clientID, strconv.Itoa(CLOSE_CONN_MSG), CONFIRMATION_MSG_SIZE)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return
	}

	end_communication_server_msg, _ := strconv.Atoi(end_connection_data)

	if end_communication_server_msg == CLOSE_CONN_MSG {
		log.Infof("[CLIENT %v] Close connection successfuly", clientID)
	} else {
		log.Infof("[CLIENT %v] Close connection with error: %v", clientID, err.Error())
	}

	communicator.shutdown()
}

// Builds and return the message to send Server and check if Player is Winner
func (winnerService *WinnerService) getPlayerMsg(player Player) string {
	var buffer bytes.Buffer
	buffer.WriteString(player.firstName)
	buffer.WriteString(MSG_SEPARATOR)
	buffer.WriteString(player.lastName)
	buffer.WriteString(MSG_SEPARATOR)
	buffer.WriteString(player.document)
	buffer.WriteString(MSG_SEPARATOR)
	buffer.WriteString(player.birthDate)
	return buffer.String()
}

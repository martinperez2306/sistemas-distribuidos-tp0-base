package common

import (
	"bytes"
	"strconv"

	log "github.com/sirupsen/logrus"
)

const MSG_SEPARATOR string = "_"

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

	data, err := communicator.sendAndWait(clientID, strconv.Itoa(msg_length), 4)

	if err != nil {
		log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
		communicator.shutdown()
		return
	}

	accepted_server_size_msg, _ := strconv.Atoi(data)

	log.Infof("[CLIENT %v] Accepted Server Size Message %d", clientID, accepted_server_size_msg)

	if accepted_server_size_msg == msg_length {
		log.Infof("[CLIENT %v] Im ok to send message data %s", clientID, msg)
		data, err := communicator.sendAndWait(clientID, msg, 1)

		if err != nil {
			log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
			communicator.shutdown()
			return
		}

		winner_server_msg, err := strconv.ParseBool(string(data))

		log.Infof("[CLIENT %v] Winner Server Message %t", clientID, winner_server_msg)

		if winner_server_msg {
			log.Infof("[CLIENT %v] IM WINNER!", clientID)
		} else {
			log.Infof("[CLIENT %v] Im not winner :(", clientID)
		}

	} else {
		log.Infof("[CLIENT %v] I cant send message data %v to server", clientID, msg)
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

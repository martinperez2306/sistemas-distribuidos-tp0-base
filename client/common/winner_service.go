package common

import (
	"bytes"
	"strconv"
	"strings"

	log "github.com/sirupsen/logrus"
)

const FILE_MSG_SEPARATOR string = ","
const SERVER_MSG_SEPARATOR string = "_"

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
func (winnerService *WinnerService) checkWinners(communicator *Communicator, clientID string, playerList []string) {

	players := winnerService.validatePlayerList(playerList)
	msg := winnerService.getPlayersMsg(players)

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
		data, err := communicator.sendAndWait(clientID, msg, msg_length) //The client receives at most the same message

		if err != nil {
			log.Infof("[CLIENT %v] Communication Error: %v", clientID, err.Error())
			communicator.shutdown()
			return
		}

		log.Infof("[CLIENT %v] Winner Server Message %s", clientID, data)

		if data == "empty" {
			log.Infof("[CLIENT %v] No winners", clientID)
		} else {
			log.Infof("[CLIENT %v] winners: %s", data)
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

func (winnerService *WinnerService) validatePlayerList(playerList []string) []Player {
	var players []Player
	for _, playerLine := range playerList {
		playerData := strings.Split(playerLine, FILE_MSG_SEPARATOR)
		player := NewPlayer(playerData[0], playerData[1], playerData[2], playerData[3])
		players = append(players, player)
	}
	return players
}

// Builds and return the message to send Server and check if Player is Winner
func (winnerService *WinnerService) getPlayersMsg(players []Player) string {
	var buffer bytes.Buffer
	for i, player := range players {
		buffer.WriteString(player.firstName)
		buffer.WriteString(SERVER_MSG_SEPARATOR)
		buffer.WriteString(player.lastName)
		buffer.WriteString(SERVER_MSG_SEPARATOR)
		buffer.WriteString(player.document)
		buffer.WriteString(SERVER_MSG_SEPARATOR)
		buffer.WriteString(player.birthDate)
		if i < (len(players) - 1) {
			buffer.WriteString("\n")
		}
	}
	return buffer.String()
}

package common

import (
	"bytes"
	"strings"

	log "github.com/sirupsen/logrus"
)

const FILE_MSG_SEPARATOR string = ","
const SERVER_MSG_SEPARATOR string = "_"

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

	data, err := communicator.request(clientID, msg)

	if err != nil {
		log.Infof("[CLIENT %v] Cant check winner: %v", clientID, err)
		return
	}

	if data == "empty" {
		log.Infof("[CLIENT %v] No winners", clientID)
	} else {
		log.Infof("[CLIENT %v] winners: %s", clientID, data)
	}
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

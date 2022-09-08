package common

import (
	"bytes"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

const FILE_DATA_SEPARATOR = ","
const SERVER_DATA_SEPARATOR = "_"
const SERVER_ENTITY_SEPARATOR = "&"

const PLAYER_DATA_SIZE = 4

const AGENCIES_WINNERS_PENDING = "PROCESS_PENDING"
const AGENCIES_WINNERS_COMPLETE = "PROCESS_FINISH"

type WinnerService struct {
	winnersClient *WinnersClient
	retryTime     time.Duration
}

// NewWinnerService Initializes a new Winner Service
func NewWinnerService(config ClientConfig) *WinnerService {
	winnerService := &WinnerService{
		winnersClient: NewWinnersClient(),
		retryTime:     config.ClientRetryInSeconds,
	}
	return winnerService
}

// Check if Player is a Winner sending message to server
// Logs Winners percentage or if no winners
func (winnerService *WinnerService) checkWinners(communicator *Communicator, clientID string, playerList []string) {

	players := winnerService.buildPlayerList(playerList)
	msg := winnerService.buildPlayersMsg(players)

	data, err := winnerService.winnersClient.getWinners(communicator, clientID, msg)

	if err != nil {
		log.Infof("[CLIENT %v] Cant check winners: %v", clientID, err)
		return
	}

	winnersPercentaje := float64(0)
	if data == "empty" {
		log.Infof("[CLIENT %v] No winners", clientID)
	} else {
		log.Infof("[CLIENT %v] Winners: %s", clientID, data)
		winnersData := strings.Split(data, SERVER_ENTITY_SEPARATOR)
		winnersFloat := float64(len(winnersData))
		playersFloat := float64(len(players))
		winnersPercentaje = winnersFloat / playersFloat
	}

	log.Infof("[CLIENT %v] %v %% winners", clientID, winnersPercentaje)
}

// Check if Player is a Winner sending message to server
// Logs Winners percentage or if no winners
func (winnerService *WinnerService) checkAgenciesWinners(communicator *Communicator, clientID string) {
	agenciesWinnerProcess := AGENCIES_WINNERS_PENDING
	for agenciesWinnerProcess == AGENCIES_WINNERS_PENDING {
		log.Infof("[CLIENT %v] Check agencies winners", clientID)
		data, err := winnerService.winnersClient.getAgenciesWinners(communicator, clientID)

		if err != nil {
			log.Infof("[CLIENT %v] Cant check agencies winners: %v", clientID, err)
			return
		}

		log.Infof("[CLIENT %v] Agencies Winner Data: %s", clientID, data)
		agenciesData := strings.Split(data, SERVER_ENTITY_SEPARATOR)

		if agenciesData[0] == AGENCIES_WINNERS_COMPLETE {
			log.Infof("[CLIENT %v] Agencies winners process is complete", clientID)
			_, agencies := agenciesData[0], agenciesData[1:]
			for agency := range agencies {
				agencyData := strings.Split(agencies[agency], SERVER_DATA_SEPARATOR)
				log.Infof("[CLIENT %v] Agency %v has %v winners", clientID, agencyData[0], agencyData[1])
			}
		} else {
			log.Infof("[CLIENT %v] Agencies winners process is pending. Waiting %v and try againg", clientID, winnerService.retryTime)
			time.Sleep(winnerService.retryTime)
		}
		agenciesWinnerProcess = agenciesData[0]
	}
}

// Builds player with given player string list
func (winnerService *WinnerService) buildPlayerList(playerList []string) []Player {
	var players []Player
	for _, playerLine := range playerList {
		playerData := strings.Split(playerLine, FILE_DATA_SEPARATOR)
		if len(playerData) == PLAYER_DATA_SIZE {
			player := NewPlayer(playerData[0], playerData[1], playerData[2], playerData[3])
			players = append(players, player)
		}
	}
	return players
}

// Builds and return the message to send to Server
func (winnerService *WinnerService) buildPlayersMsg(players []Player) string {
	var buffer bytes.Buffer
	for i, player := range players {
		buffer.WriteString(player.firstName)
		buffer.WriteString(SERVER_DATA_SEPARATOR)
		buffer.WriteString(player.lastName)
		buffer.WriteString(SERVER_DATA_SEPARATOR)
		buffer.WriteString(player.document)
		buffer.WriteString(SERVER_DATA_SEPARATOR)
		buffer.WriteString(player.birthDate)
		if i < (len(players) - 1) {
			buffer.WriteString(SERVER_ENTITY_SEPARATOR)
		}
	}
	return buffer.String()
}

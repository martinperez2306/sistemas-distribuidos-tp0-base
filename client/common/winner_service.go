package common

import (
	"bytes"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

const FILE_PLAYER_DATA_SEPARATOR string = ","
const SERVER_PLAYER_DATA_SEPARATOR string = "_"
const PLAYER_SEPARATOR = "&"

const PLAYER_DATA_SIZE = 4

const AGENCIES_WINNERS_PENDING = "PROCESS_PENDING"
const AGENCIES_WINNERS_COMPLETE = "PROCESS_FINISH"

const TIME_TO_TRY = 60 * time.Second

type WinnerService struct {
	winnersClient *WinnersClient
}

// NewWinnerService Initializes a new Winner Service
func NewWinnerService() *WinnerService {
	winnerService := &WinnerService{
		winnersClient: NewWinnersClient(),
	}
	return winnerService
}

// Check if Player is a Winner sending message to server with communicator
func (winnerService *WinnerService) checkWinners(communicator *Communicator, clientID string, playerList []string) {

	players := winnerService.validatePlayerList(playerList)
	msg := winnerService.getPlayersMsg(players)

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
		winnersData := strings.Split(data, PLAYER_SEPARATOR)
		winnersFloat := float64(len(winnersData))
		playersFloat := float64(len(players))
		winnersPercentaje = winnersFloat / playersFloat
	}

	log.Infof("[CLIENT %v] %v %% winners", clientID, winnersPercentaje)
}

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
		agenciesData := strings.Split(data, PLAYER_SEPARATOR)

		if agenciesData[0] == AGENCIES_WINNERS_COMPLETE {
			log.Infof("[CLIENT %v] Agencies winners process is complete", clientID)
			_, agencies := agenciesData[0], agenciesData[1:]
			for agency := range agencies {
				agencyData := strings.Split(agencies[agency], SERVER_PLAYER_DATA_SEPARATOR)
				log.Infof("[CLIENT %v] Agency %v has %v winners", clientID, agencyData[0], agencyData[1])
			}
		} else {
			log.Infof("[CLIENT %v] Agencies winners process is pending. Waiting %v and try againg", clientID, TIME_TO_TRY)
			time.Sleep(TIME_TO_TRY)
		}
		agenciesWinnerProcess = agenciesData[0]
	}
}

func (winnerService *WinnerService) validatePlayerList(playerList []string) []Player {
	var players []Player
	for _, playerLine := range playerList {
		playerData := strings.Split(playerLine, FILE_PLAYER_DATA_SEPARATOR)
		if len(playerData) == PLAYER_DATA_SIZE {
			player := NewPlayer(playerData[0], playerData[1], playerData[2], playerData[3])
			players = append(players, player)
		}
	}
	return players
}

// Builds and return the message to send Server and check if Player is Winner
func (winnerService *WinnerService) getPlayersMsg(players []Player) string {
	var buffer bytes.Buffer
	for i, player := range players {
		buffer.WriteString(player.firstName)
		buffer.WriteString(SERVER_PLAYER_DATA_SEPARATOR)
		buffer.WriteString(player.lastName)
		buffer.WriteString(SERVER_PLAYER_DATA_SEPARATOR)
		buffer.WriteString(player.document)
		buffer.WriteString(SERVER_PLAYER_DATA_SEPARATOR)
		buffer.WriteString(player.birthDate)
		if i < (len(players) - 1) {
			buffer.WriteString(PLAYER_SEPARATOR)
		}
	}
	return buffer.String()
}

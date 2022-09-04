package common

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID              string
	ServerAddress   string
	CommunicationTO time.Duration
}

// Client Entity
type Client struct {
	config        ClientConfig
	communicator  *Communicator
	winnerService *WinnerService
	player        Player
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, player Player) *Client {
	communicator := NewCommunicator(config)
	winnerService := NewWinnerService()
	client := &Client{
		config:        config,
		player:        player,
		communicator:  communicator,
		winnerService: winnerService,
	}
	return client
}

// StartClient Send messages to the server
func (client *Client) StartClient() {
	// Create the connection the server
	// Send Player data to verify winner
	client.communicator.createClientSocket(*client)

	go client.gracefulShutdown()

	client.winnerService.checkWinner(client.communicator, client.config.ID, client.player)
}

func (client *Client) gracefulShutdown() {
	exit := make(chan os.Signal, 1)
	// catch SIGETRM or SIGINTERRUPT
	signal.Notify(exit, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-exit
		fmt.Println("Sutting down gracefully.")
		log.Infof("[CLIENT %v] Caught shutdown signal", client.config.ID)
		log.Infof("[CLIENT %v] Proceed to shutdown client gracefully", client.config.ID)
		log.Infof("[CLIENT %v] Closing connection", client.config.ID)
		client.communicator.shutdown()
		log.Infof("[CLIENT %v] Client stop running", client.config.ID)
		os.Exit(0)
	}()
}

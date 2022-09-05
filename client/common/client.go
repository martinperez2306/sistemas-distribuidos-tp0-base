package common

import (
	"bufio"
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
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	communicator := NewCommunicator(config)
	winnerService := NewWinnerService()
	client := &Client{
		config:        config,
		communicator:  communicator,
		winnerService: winnerService,
	}
	return client
}

// StartClient Send messages to the server
func (client *Client) StartClient() {
	//Reads client data file
	filepath := "./.data/"
	filename := fmt.Sprintf("dataset-%s.csv", client.config.ID)
	filepath = filepath + filename
	log.Infof("[CLIENT %v] Read file %s", client.config.ID, filepath)

	playerLines, err := client.getLinesFromFile(filepath)

	if err != nil {
		log.Infof("[CLIENT %v] No data to request. Err: %v", client.config.ID, err)
		os.Exit(0)
	}

	// Create the connection the server
	// Send Player data to verify winner
	client.communicator.createClientSocket(*client)

	go client.gracefulShutdown()

	client.winnerService.checkWinners(client.communicator, client.config.ID, playerLines)
}

func (client *Client) getLinesFromFile(filepath string) ([]string, error) {
	file, err := os.Open(filepath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
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

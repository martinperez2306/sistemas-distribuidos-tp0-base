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

// Client Entity that encapsulates how
type Client struct {
	config       ClientConfig
	communicator *Communicator
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	communicator := NewCommunicator(config)
	client := &Client{
		config:       config,
		communicator: communicator,
	}
	return client
}

// StartClient Send messages to the client until some time threshold is met
func (client *Client) StartClient() {
	// Create the connection the server in every loop iteration. Send an
	// autoincremental msgID to identify every message sent
	client.communicator.createClientSocket(*client)

	go client.gracefulShutdown()

	msg := "Martin_Perez_12345678_1995-06-23"

	client.communicator.check_winner(client.config.ID, msg)

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

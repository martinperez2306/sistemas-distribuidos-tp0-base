package common

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"[CLIENT %v] Could not connect to server. Error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// Create the connection the server in every loop iteration. Send an
	// autoincremental msgID to identify every message sent
	c.createClientSocket()
	msgID := 1

	exit := make(chan os.Signal, 1)
	// catch SIGETRM or SIGINTERRUPT
	signal.Notify(exit, os.Interrupt, syscall.SIGTERM)

	timeout := time.After(c.config.LoopLapse)

loop:
	// Send messages if the loopLapse threshold has been not surpassed
	for {
		select {
		case <-exit:
			log.Infof("[CLIENT %v] Caught shutdown signal", c.config.ID)
			log.Infof("[CLIENT %v] Proceed to shutdown client gracefully", c.config.ID)
			break loop
		case <-timeout:
			break loop
		case <-time.After(1 * time.Second): // Wait a time between sending one message and the next one
			// Send
			fmt.Fprintf(
				c.conn,
				"[CLIENT %v] Message N°%v sent\n",
				c.config.ID,
				msgID,
			)
			msg, err := bufio.NewReader(c.conn).ReadString('\n')
			msgID++

			if err != nil {
				log.Errorf(
					"[CLIENT %v] Error reading from socket. %v.",
					c.config.ID,
					err,
				)
				c.conn.Close()
				return
			}
			log.Infof("[CLIENT %v] Message from server: %v", c.config.ID, msg)

			time.Sleep(c.config.LoopPeriod)

			// Recreate connection to the server
			c.conn.Close()
			c.createClientSocket()
		default:
		}

	}

	log.Infof("[CLIENT %v] Closing connection", c.config.ID)
	c.conn.Close()
	log.Infof("[CLIENT %v] Client stop running", c.config.ID)
}

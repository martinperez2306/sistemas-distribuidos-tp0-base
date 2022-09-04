package common

import (
	"fmt"
	"io"
	"net"
	"os"
	"os/signal"
	"strconv"
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
	msg := "Martin_Perez_12345678_1995-06-23"
	msg_length := len(msg)
	log.Infof("Length %v", msg_length)

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
		default: // Wait a time between sending one message and the next one
			// Send
			fmt.Fprintf(c.conn, "%d", msg_length)
			read_buff := make([]byte, 4)
			n, err := c.conn.Read(read_buff)
			data := make([]byte, 0)
			data = append(data, read_buff[:n]...)

			if err != nil {
				log.Errorf(
					"[CLIENT %v] Error reading from socket. %v.",
					c.config.ID,
					err,
				)
				c.conn.Close()
				return
			}

			log.Infof("[CLIENT %v] Message from server: %v", c.config.ID, data)

			server_msg_int, _ := strconv.Atoi(string(data))

			log.Infof("[CLIENT %v] Message from server %d", c.config.ID, server_msg_int)

			if server_msg_int == msg_length {
				fmt.Fprintf(c.conn, "%v", msg)
			}

			read_buff_2 := make([]byte, 1)
			data2 := make([]byte, 0)
		loop2:
			for timeout2 := time.After(3 * time.Second); ; { //establecer TO
				select {
				case <-timeout2:
					break loop2
				default:
				}

				n2, err2 := c.conn.Read(read_buff_2)
				data2 = append(data2, read_buff_2[:n2]...)

				if err2 != nil {
					if err2 != io.EOF {
						log.Printf("Read error: %s", err2)
						c.conn.Close()
						return
					}
				} else {
					break loop2
				}

			}

			log.Infof("[CLIENT %v] Message from server: %v", c.config.ID, data2)

			server_msg_2, err := strconv.ParseBool(string(data2))

			log.Infof("[CLIENT %v] Message from server %t", c.config.ID, server_msg_2)

			if server_msg_2 {
				log.Infof("[CLIENT %v] IM WINNER!", c.config.ID)
			} else {
				log.Infof("[CLIENT %v] Im not winner :(", c.config.ID)
			}

			time.Sleep(c.config.LoopPeriod)

			// Recreate connection to the server
			c.conn.Close()
			c.createClientSocket()
		}

	}

	log.Infof("[CLIENT %v] Closing connection", c.config.ID)
	c.conn.Close()
	log.Infof("[CLIENT %v] Client stop running", c.config.ID)
}

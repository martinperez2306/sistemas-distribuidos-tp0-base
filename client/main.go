package main

import (
	"fmt"
	"strings"
	"time"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/viper"

	"github.com/7574-sistemas-distribuidos/docker-compose-init/client/common"
)

// InitConfig Function that uses viper library to parse configuration parameters.
// Viper is configured to read variables from both environment variables and the
// config file ./config.yaml. Environment variables takes precedence over parameters
// defined in the configuration file. If some of the variables cannot be parsed,
// an error is returned
func InitConfig() (*viper.Viper, error) {
	v := viper.New()

	// Configure viper to read env variables with the CLI_ prefix
	v.AutomaticEnv()
	v.SetEnvPrefix("cli")
	// Use a replacer to replace env variables underscores with points. This let us
	// use nested configurations in the config file and at the same time define
	// env variables for the nested configurations
	v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	// Add env variables supported
	v.BindEnv("id")
	v.BindEnv("server", "address")
	v.BindEnv("communication", "timeout")
	v.BindEnv("log", "level")

	// Try to read configuration from config file. If config file
	// does not exists then ReadInConfig will fail but configuration
	// can be loaded from the environment variables so we shouldn't
	// return an error in that case
	v.SetConfigFile("./config/config.yaml")
	if err := v.ReadInConfig(); err != nil {
		fmt.Printf("Configuration could not be read from config file. Using env variables instead")
	}

	// Parse time.Duration variables and return an error if those variables cannot be parsed
	if _, err := time.ParseDuration(v.GetString("communication.timeout")); err != nil {
		return nil, errors.Wrapf(err, "Could not parse CLI_COMMUNICATION_TIMEOUT env var as time.Duration.")
	}

	return v, nil
}

// InitLogger Receives the log level to be set in logrus as a string. This method
// parses the string and set the level to the logger. If the level string is not
// valid an error is returned
func InitLogger(logLevel string) error {
	level, err := logrus.ParseLevel(logLevel)
	if err != nil {
		return err
	}

	logrus.SetLevel(level)
	return nil
}

// PrintConfig Print all the configuration parameters of the program.
// For debugging purposes only
func PrintConfig(v *viper.Viper) {
	logrus.Infof("Client configuration")
	logrus.Infof("Client ID: %s", v.GetString("id"))
	logrus.Infof("Server Address: %s", v.GetString("server.address"))
	logrus.Infof("Communication Timeout: %v", v.GetDuration("communication.timeout"))
	logrus.Infof("Log Level: %s", v.GetString("log.level"))
	logrus.Infof("First Name: %s", v.GetString("first.name"))
	logrus.Infof("Last Name: %s", v.GetString("last.name"))
	logrus.Infof("Document: %s", v.GetString("document"))
	logrus.Infof("Birth Date: %s", v.GetString("birth.date"))
}

func main() {
	v, err := InitConfig()
	if err != nil {
		log.Fatalf("%s", err)
	}

	if err := InitLogger(v.GetString("log.level")); err != nil {
		log.Fatalf("%s", err)
	}

	// Print program config with debugging purposes
	PrintConfig(v)

	clientConfig := common.ClientConfig{
		ServerAddress:   v.GetString("server.address"),
		ID:              v.GetString("id"),
		CommunicationTO: v.GetDuration("communication.timeout"),
	}

	player := common.NewPlayer(v.GetString("first.name"), v.GetString("last.name"), v.GetString("document"), v.GetString("birth.date"))
	client := common.NewClient(clientConfig, player)

	client.StartClient()
}

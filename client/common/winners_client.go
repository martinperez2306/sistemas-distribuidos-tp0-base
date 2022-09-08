package common

import (
	"bytes"
	"fmt"
)

const REQUEST_CLIENT_FORMAT = "REQUEST_CLI[%s]"
const REQUEST_NAME_FORMAT = "REQUEST_NAME[%s]"
const REQUEST_BODY_FORMAT = "REQUEST_BODY[%s]"

const GET_WINNERS = "GET_WINNERS"
const GET_AGENCIES_WINNERS = "GET_AGENCIES_WINNERS"

type WinnersClient struct {
}

// NewWinnerService Initializes a new Winners Client
func NewWinnersClient() *WinnersClient {
	winnersClient := &WinnersClient{}
	return winnersClient
}

func (winnersClient *WinnersClient) getWinners(communicator *Communicator, clientID string, body string) (string, error) {
	getWinnersMessage := winnersClient.getRequestMessage(clientID, GET_WINNERS, body)
	return communicator.request(clientID, getWinnersMessage)
}

func (winnersClient *WinnersClient) getRequestMessage(client string, name string, body string) string {
	requestClient := fmt.Sprintf(REQUEST_CLIENT_FORMAT, client)
	requestName := fmt.Sprintf(REQUEST_NAME_FORMAT, name)
	requestBody := fmt.Sprintf(REQUEST_BODY_FORMAT, body)
	var buffer bytes.Buffer
	buffer.WriteString(requestClient)
	buffer.WriteString(requestName)
	buffer.WriteString(requestBody)
	return buffer.String()
}

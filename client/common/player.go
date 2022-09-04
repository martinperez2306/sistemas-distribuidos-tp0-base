package common

// Communicator Entity
type Player struct {
	firstName string
	lastName  string
	document  string
	birthDate string
}

// NewPlayer Initializes a new player receiving the player information
// as parameters
func NewPlayer(first_name string, last_name string, document string, birth_date string) Player {
	player := Player{
		firstName: first_name,
		lastName:  last_name,
		document:  document,
		birthDate: birth_date,
	}
	return player
}

import datetime


""" Winners storage location. """
STORAGE = "./winners"

CONTESTANT_SEPARATOR = "_"

CONTESTANT_BIRTHDATE_FORMAT = "%Y-%m-%d"

CONTESTANT_DATA_SEPARATOR = "|"

""" Contestant data model. """
class Contestant:
	def __init__(self, first_name, last_name, document, birthdate, agency):
		""" Birthdate must be passed with format: 'YYYY-MM-DD'. """
		self.first_name = first_name
		self.last_name = last_name
		self.document = document
		self.birthdate = datetime.datetime.strptime(birthdate, '%Y-%m-%d')
		self.agency = agency
		
	def __hash__(self):
		return hash((self.first_name, self.last_name, self.document, self.birthdate))

	def to_string(self):
		return self.first_name + CONTESTANT_SEPARATOR + self.last_name + CONTESTANT_SEPARATOR + self.document + CONTESTANT_SEPARATOR + self.birthdate.strftime(CONTESTANT_BIRTHDATE_FORMAT)


""" Checks whether a contestant is a winner or not. """
def is_winner(contestant: Contestant) -> bool:
	# Simulate strong computation requirements using a sleep to increase function retention and force concurrency.
	#time.sleep(0.001)
	return hash(contestant) % 17 == 0


""" Persist the information of each winner in the STORAGE file. Not thread-safe/process-safe. """
def persist_winners(winners: 'list[Contestant]') -> None:
	with open(STORAGE, 'a+') as file:
		for winner in winners:
			file.write(f'First name: {winner.first_name} | Last name: {winner.last_name} | Document: {winner.document} | Date of Birth: {winner.birthdate.strftime(CONTESTANT_BIRTHDATE_FORMAT)} | Agency: {winner.agency}\n')

class Agency:
	def __init__(self, id: int, winners: 'list[Contestant]'):
		self.id = id
		self.winners_count = len(winners)

	def to_string(self):
		return str(self.id) + CONTESTANT_SEPARATOR + str(self.winners_count)
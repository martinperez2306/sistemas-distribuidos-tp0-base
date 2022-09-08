from multiprocessing import Semaphore

class WinnersTrack:
    def __init__(self):
        self._processing_clients = list()
        self._track_semaphore = Semaphore(1)
        self._max_clients_tracked = 0

    def track_init_process(self, client: str):
        self._track_semaphore.acquire()
        client_id = int(client)
        if (self._max_clients_tracked < client_id):
            self._max_clients_tracked = client_id
        self._processing_clients.append(client)
        self._track_semaphore.release()

    def track_finish_process(self, client: str):
        self._track_semaphore.acquire()
        self._processing_clients = filter(lambda c: c != client, self._processing_clients)
        self._track_semaphore.release()

    def processing(self) -> bool:
        self._track_semaphore.acquire()
        processing = (len(self._processing_clients) > 0)
        self._track_semaphore.release()
        return processing

    def get_pending_process_count(self) -> int:
        self._track_semaphore.acquire()
        processing = len(self._processing_clients)
        self._track_semaphore.release()
        return processing

    def get_max_clients_tracked(self):
        return self._max_clients_tracked
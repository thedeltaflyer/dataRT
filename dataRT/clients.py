from uuid import uuid4
from gevent.pool import Pool

from .logs import logger


class Clients(object):
    def __init__(self):
        self._clients = {}
        self._client_data = {}
        self._send_pool = Pool(50)
        logger.debug('Created Clients Object')

    def get_id(self, client):
        if client in self._clients:
            logger.debug('Found ID {} for {}'.format(self._clients[client], client))
            return self._clients[client]
        elif client in self._client_data:
            logger.debug('Provided Client is valid ID: {}'.format(client))
            return client
        logger.debug('Client {} does not exist!'.format(client))
        return None  # Client does not exist!

    def get_client(self, client):
        if client in self._clients:
            logger.debug('Provided Client is valid: {}'.format(client))
            return client
        elif client in self._client_data:
            logger.debug('Provided ID "{}" is valid Client'.format(client))
            return self._client_data[client]['client']
        logger.debug('Client {} does not exist!'.format(client))
        return None  # Client does not exist!

    def add(self, client):
        logger.debug('Adding Client: {}'.format(client))
        if client not in self._clients:
            uuid = str(uuid4())
            logger.debug('Using new ID: {}'.format(uuid))
            self._clients[client] = uuid
            self._client_data[uuid] = {'client': client}

    def remove(self, client):
        logger.debug('Removing Client: {}'.format(client))
        if client not in self._clients:
            if client in self._client_data:
                uuid = client
                client = self._client_data[client]
            else:
                logger.warning('Unable to Find Client to Remove: {}'.format(client))
                return False
        else:
            uuid = self._clients[client]
        _ = self._clients.pop(client)
        _ = self._client_data.pop(uuid)
        return True

    def send(self, client, message):
        if client in self._clients:
            pass
        elif client in self._client_data:
            client = self._client_data[client]['client']
        else:
            logger.warning('Client "{}" does not exist to send message: {}'.format(client, message))
            return False
        logger.debug('Sending message to client {}: {}'.format(client, message))
        self._send_pool.spawn(self._send, client, message)
        return True

    def _send(self, client, message):
        client = self.get_client(client)
        if client.closed:
            logger.warning('Client "{}" was already closed, cannot send message: {}'.format(client, message))
            self.remove(client)
            return
        client.send(message)
        logger.debug('Send message to {}: {}'.format(client, message))

    def send_all(self, message):
        logger.debug('Sending message to ALL clients: {}'.format(message))
        for client in self._clients:
            self.send(client, message)

    @property
    def clients(self):
        return self._clients.keys()

    @property
    def ids(self):
        return self._client_data.keys()

    def __len__(self):
        return len(self._clients)

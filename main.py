#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from parser import ClientParser


class Server(DatagramProtocol):
    def __init__(self, host, port):
        self.srv_host = host
        self.srv_port = port
        self.clients = {}

    def datagramReceived(self, data, (host, port)):
        """
        received from client
        """
        client = self.get_or_create_client(host, port)
        client.client_to_server_pkg(data)

    def get_or_create_client(self, host, port):
        addr_str = '%s::%s' % (host, port)
        if addr_str not in self.clients:
            client = ClientParser(host, port, self)
            self.clients[addr_str] = client
            reactor.listenUDP(0, client)
        else:
            client = self.clients[addr_str]
        return client

    def send_to_client(self, data, host, port):
        self.transport.write(data, (host, port))


if __name__ == '__main__':
    reactor.listenUDP(8304, Server('127.0.0.1', 8303))
    reactor.run()
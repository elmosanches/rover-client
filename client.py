import sys
from urlparse import urlparse
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver


class ArduinoProtocol(LineReceiver):

    counter = 0

    def connectionMade(self):
        print 'Arduino device: ', self, ' is connected.'

    def lineReceived(self, line):
        print line

        self.counter += 1

        """
        sending commands to SerialPort
        """
        # if not self.counter % 5:
        #     print self.counter
        #     self.sendLine("0:0:1")


class ServerProtocol(LineReceiver):

    def lineReceived(self, line):
        print line

        #validate line
        #send line to arduino


class ServerFactory(Factory):

    def buildProtocol(self, addr):
        p = ServerProtocol()
        p.factory = self
        return p


if __name__ == '__main__':
    SERVER_ADDRESS = '37.59.112.176'
    SERVER_PORT = 8123

    arduino = ArduinoProtocol()

    SerialPort(arduino, '/dev/ttyUSB0', reactor, baudrate='9600')

    # create factory protocol and application
    server_factory = ServerFactory()

    # connect factory to this host and port
    # reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, server_factory)

    reactor.run()

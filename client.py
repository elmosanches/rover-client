import sys
from urlparse import urlparse
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver


class ArduinoProtocol(LineReceiver):

    server = None

    def connectionMade(self):
        print 'Arduino device: ', self, ' is connected.'

    def lineReceived(self, line):
        print "line received from arduino: ",line

        #send it to server
        self.server.sendLine(line)


class ServerProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.factory.arduino = arduino
        self.factory.arduino.server = self

    def lineReceived(self, line):
        print "line received from server: ",line

        #TODO validate line

        #send valid line to arduino
        self.factory.arduino.sendLine(line)

    def connectionMade(self):
        self.sendLine("DC:rover01")


class ServerFactory(ClientFactory):

    def __init__(self, arduino):
        self.arduino = arduino

    def buildProtocol(self, addr):
        p = ServerProtocol(self)
        return p

    def clientConnectionFailed(self, connector, reason):
        print "connection faile"
        print reason

    def clientConnectionLost(self, connector, reason):
        print "connection was lost"
        print reason
        reactor.stop()


if __name__ == '__main__':
    SERVER_ADDRESS = 'localhost'
    # SERVER_ADDRESS = '37.59.112.176'
    SERVER_PORT = 8123

    arduino = ArduinoProtocol()

    SerialPort(arduino, '/dev/ttyUSB0', reactor, baudrate='9600')

    # create factory protocol and application
    server_factory = ServerFactory(arduino)

    # connect factory to this host and port
    reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, server_factory)

    reactor.run()

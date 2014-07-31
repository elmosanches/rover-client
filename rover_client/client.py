import sys

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver


class ArduinoProtocol(LineReceiver):

    server = None

    def connectionMade(self):
        log.msg('Arduino device: %s is connected', self)

    def lineReceived(self, line):
        log.msg("line received from arduino: ", line)

        #send it to server
        self.server.sendLine(line)


class ServerProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.factory.arduino.server = self

    def lineReceived(self, line):
        log.msg("line received from server: ", line)

        #TODO validate line
        #check for error communicates from server

        if line.startswith('SE:'):
            log.err('ERROR: {}'.format(line))
            return

        #send valid line to arduino
        self.factory.arduino.sendLine(line)
        log.msg('sent to arduino %s', line)

    def connectionMade(self):
        self.sendLine("DC:{}".format(self.factory.device_name))


class ServerFactory(ClientFactory):

    def __init__(self, name, arduino):
        self.device_name = name
        self.arduino = arduino

    def buildProtocol(self, addr):
        p = ServerProtocol(self)
        return p

    def clientConnectionFailed(self, connector, reason):
        log.err("connection faile: %s", reason)

    def clientConnectionLost(self, connector, reason):
        log.err("connection was lost: %s", reason)

        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    DEVICE_NAME = 'rover01'

    SERVER_ADDRESS = 'localhost'
    # SERVER_ADDRESS = '37.59.112.176'
    SERVER_PORT = 8123

    arduino = ArduinoProtocol()

    SerialPort(arduino, '/dev/ttyUSB0', reactor, baudrate='9600')

    # create factory protocol and application
    server_factory = ServerFactory(DEVICE_NAME, arduino)

    # connect factory to this host and port
    reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, server_factory)

    reactor.run()

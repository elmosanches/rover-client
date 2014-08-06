import sys
import argparse

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver


class ArduinoProtocol(LineReceiver):

    server = None
    serial_port = None
    connected = False

    TIMEOUT = 1.0

    def __init__(self, server_protocol):
        self.server = server_protocol
        self._connect_serial_port()

    def connectionMade(self):
        log.msg('Arduino device: %s is connected', self)

    def connectionLost(self, reason):
        log.msg('Arduino device: %s disconnected', self)
        self.server.sendLine('RE:-1:-100:0')
        self.serial_port.loseConnection()

        # self._timeout = reactor.callLater(self.TIMEOUT, self.try_reconnect)

    def lineReceived(self, line):
        log.msg("line received from arduino: ", line)

        #send it to server
        if self.server is not None:
            self.server.sendLine('RE:' + line)

    def try_reconnect(self):
        self._connect_serial_port()

    def _connect_serial_port(self):
        try:
            self.serial_port = SerialPort(self, '/dev/ttyUSB0',
                                        reactor, baudrate='9600')
        except Exception as e:
            log.err("Cannot connect to serial port: ", e)
            self._timeout = reactor.callLater(self.TIMEOUT, self.try_reconnect)


class ServerProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory

    def lineReceived(self, line):
        log.msg("line received from server: ", line)

        command = self.get_command(line)
        body = self.get_body(line)

        if command == 'SE':
            log.err('ERROR: {}'.format(line))
            return

        elif command == 'RE':
            #send valid line to arduino
            self.factory.arduino.sendLine(body)
            log.msg('sent to arduino %s', body)
        else:
            log.err('unsupported command EROOR {}'.format(line))

    def connectionMade(self):
        self.sendLine("DC:{}".format(self.factory.device_name))
        self.arduino = ArduinoProtocol(self)

    def connectionLost(self, reason):
        #stop motor
        self.arduino.sendLine('0:1:1')

    def get_command(self, line):
        return line[:2]

    def get_body(self, line):
        return line[3:]


class ServerFactory(ClientFactory):

    def __init__(self, name):
        self.device_name = name

    def buildProtocol(self, addr):
        p = ServerProtocol(self)
        return p

    def clientConnectionFailed(self, connector, reason):
        self.connector = connector

        log.err("connection failed: ", reason)
        self._timeout = reactor.callLater(1, self.try_reconnect)
        # connector.connect()

    def clientConnectionLost(self, connector, reason):
        self.connector = connector
        log.err("connection was lost: ", reason)

        self._timeout = reactor.callLater(1, self.try_reconnect)

    def try_reconnect(self):
        if self.connector.state == 'disconnected':
            self.connector.connect()
            self._timeout = reactor.callLater(1, self.try_reconnect)


def main():
    log.startLogging(sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("server_address", help="internet address of the server to connect. Required format <IP>:<PORT>")
    parser.add_argument("device_name", help="name that will be send to server while connecting")
    args = parser.parse_args()

    SERVER_ADDRESS = args.server_address.split(':')[0]
    SERVER_PORT = int(args.server_address.split(':')[1])
    DEVICE_NAME = args.device_name

    # create factory protocol and application
    server_factory = ServerFactory(DEVICE_NAME)

    # connect factory to this host and port
    reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, server_factory)

    reactor.run()


if __name__ == '__main__':
    main()

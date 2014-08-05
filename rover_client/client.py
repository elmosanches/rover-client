import sys
import argparse

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver


#@TODO
"""
-detect arudino failure
-communicate arduino failure to connected endpoint
"""


class ArduinoProtocol(LineReceiver):

    server = None

    def connectionMade(self):
        log.msg('Arduino device: %s is connected', self)

    def lineReceived(self, line):
        log.msg("line received from arduino: ", line)

        #send it to server
        self.server.sendLine('RE:' + line)


class ServerProtocol(LineReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.factory.arduino.server = self

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

    def get_command(self, line):
        return line[:2]

    def get_body(self, line):
        return line[3:]


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
        #@TODO
        # attempt to reconnect every 'reconnect time'


def main():
    log.startLogging(sys.stdout)

    parser = argparse.ArgumentParser()
    parser.add_argument("server_address", help="internet address of the server to connect. Required format <IP>:<PORT>")
    parser.add_argument("device_name", help="name that will be send to server while connecting")
    args = parser.parse_args()

    SERVER_ADDRESS = args.server_address.split(':')[0]
    SERVER_PORT = int(args.server_address.split(':')[1])
    DEVICE_NAME = args.device_name

    arduino = ArduinoProtocol()
    SerialPort(arduino, '/dev/ttyUSB0', reactor, baudrate='9600')

    # create factory protocol and application
    server_factory = ServerFactory(DEVICE_NAME, arduino)

    # connect factory to this host and port
    reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, server_factory)

    reactor.run()


if __name__ == '__main__':
    main()

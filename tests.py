from twisted.trial import unittest
from twisted.test import proto_helpers

from rover_client.client import ServerFactory
from rover_client.client import ArduinoProtocol


class MockArduino:
    server = None
    sent_lines = []

    def sendLine(self, line):
        self.sent_lines.append(line)


class ServerFactoryTest(unittest.TestCase):

    DEVICE_NAME = 'mock-rover'

    def setUp(self):

        self.mock_arduino = MockArduino()

        factory = ServerFactory(self.DEVICE_NAME, self.mock_arduino)
        self.proto = factory.buildProtocol(('127.0.0.1', 0))
        self.mock_arduino.sever = self.proto
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

    def test_connectionMade(self):

        EXPECTED = 'DC:{}\r\n'.format(self.DEVICE_NAME)

        result = self.tr.value()
        self.assertEqual(self.tr.value(), EXPECTED)

    def test_lineRecived(self):

        END_LINE = '\r\n'
        REQUEST = 'RE:0:0:0' + END_LINE
        ARDUINO_EXPECTED = '0:0:0'
        self.proto.dataReceived(REQUEST)
        self.assertEqual(self.mock_arduino.sent_lines[0], ARDUINO_EXPECTED)


class ArduinoProtocolTest(unittest.TestCase):

    class MockServer:
        sent_lines = []
        def sendLine(self, line):
            self.sent_lines.append(line)

    def setUp(self):
        self.mock_server = self.MockServer()

        self.tr = proto_helpers.StringTransport()
        self.proto = ArduinoProtocol()
        self.proto.server = self.mock_server
        self.proto.makeConnection(self.tr)

    def test_lineRecived(self):

        END_LINE = '\r\n'
        REQUEST = '0:0:0' + END_LINE
        SERVER_EXPECTED = 'RE:0:0:0'
        self.proto.dataReceived(REQUEST)
        self.assertEqual(self.mock_server.sent_lines[0], SERVER_EXPECTED)

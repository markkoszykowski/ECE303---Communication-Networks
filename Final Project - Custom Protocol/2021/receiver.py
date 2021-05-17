# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

MAX_SEQUENCE_NUMBER = 256


class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info(
            "Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                data = self.simulator.u_receive()  # receive data
                self.logger.info("Got data from socket: {}".format(
                    data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                sys.stdout.write(data)
                self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()


class OurReceiver(BogoReceiver):

    def __init__(self, timeout=0.1):
        super(OurReceiver, self).__init__()
        self.timeout = timeout
        self.simulator.rcvr_socket.settimeout(self.timeout)
        self.recent_ack = bytearray([0, 0])

    # check the checksum
    @staticmethod
    def check_checksum(data):
        checksum = ~data[0]
        for i in xrange(1, len(data)):
            checksum = checksum ^ data[i]

        return checksum == -1

    def receive(self):
        self.logger.info(
            "Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        # set parameters for corruptness
        duplicates = 0
        previous_ack_number = -1
        while True:
            try:
                data = self.simulator.u_receive()
                # bring down timeout for received packet
                if self.timeout > 0.1:
                    duplicates = 0
                    self.timeout = self.timeout - 0.1
                    self.simulator.rcvr_socket.settimeout(self.timeout)
                ack_number = 0
                # verify checksum -> store previous ack number & write to output
                if self.check_checksum(data):
                    ack_number = (data[1] + len(data[2:])) % MAX_SEQUENCE_NUMBER
                    if data[1] == previous_ack_number or previous_ack_number == -1:
                        sys.stdout.write(data[2:])
                        sys.stdout.flush()
                        previous_ack_number = ack_number
                # checksum is just the ACK number
                checksum = ack_number
                send_array = bytearray([checksum, ack_number])
                # store ACK and send
                self.recent_ack = send_array
                self.simulator.u_send(send_array)
            # socket timeout -> send most recent ACK
            except socket.timeout:
                self.simulator.u_send(self.recent_ack)
                duplicates += 1
                if duplicates == 3:
                    duplicates = 0
                    self.timeout *= 2
                    if self.timeout > 10:
                        sys.exit()
                    self.simulator.rcvr_socket.settimeout(self.timeout)


if __name__ == "__main__":
    # test out BogoReceiver
    # rcvr = BogoReceiver()
    # rcvr.receive()
    # use OurReceiver
    rcvr = OurReceiver()
    rcvr.receive()

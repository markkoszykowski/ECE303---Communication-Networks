# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys

import math
import random

MAX_SEQUENCE_NUMBER = 256


class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info(
            "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


class OurSender(BogoSender):

    def __init__(self, max_segment_size=250, timeout=0.1):
        super(OurSender, self).__init__()
        self.MSS = max_segment_size
        self.timeout = timeout
        self.simulator.sndr_socket.settimeout(self.timeout)
        self.partition_start = 0
        self.partition_end = self.MSS
        self.sequence_number = random.randint(0, MAX_SEQUENCE_NUMBER - 1)

    # produce a checksum value
    @staticmethod
    def checksum(data):
        checksum = 0
        for i in xrange(len(data)):
            checksum = checksum ^ data[i]

        return checksum

    # check the checksum
    @staticmethod
    def check_checksum(ack):
        checksum = ~ack[0]
        for i in xrange(1, len(ack)):
            checksum = checksum ^ ack[i]

        return checksum == -1

    # assign sequence numbers to segments
    def assign_sequence_number(self):
        self.sequence_number = (self.sequence_number + self.MSS) % MAX_SEQUENCE_NUMBER
        return self.sequence_number

    # divide whole data into segments of size "max_seqment_size/MSS"
    def segment_data(self, data):
        for i in range(int(math.ceil(len(data) / float(self.MSS)))):
            yield data[self.partition_start:self.partition_end]
            self.partition_start += self.MSS
            self.partition_end += self.MSS

    def send(self, data):
        self.logger.info(
            "Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        # redefine bounds for splitting into segments
        self.partition_start = 0
        self.partition_end = self.MSS
        # set parameters for corruptness
        resend = False
        sent = False
        duplicates = 0
        for segment in self.segment_data(data):
            try:
                # initial attempt to send a segment
                if not resend:
                    send_array = bytearray([0, self.assign_sequence_number()])
                    send_array += segment
                    send_array[0] = self.checksum(send_array)
                    self.simulator.u_send(send_array)

                while True:
                    ack = self.simulator.u_receive()
                    # verify checksum -> checks whether segment was corrupt
                    if self.check_checksum(ack):
                        # current segment was not acknowledged -> resend
                        if ack[1] == self.sequence_number:
                            sent = True
                            self.simulator.u_send(send_array)
                        # current segment was acknowledged -> break
                        elif ack[1] == (self.sequence_number + len(segment)) % MAX_SEQUENCE_NUMBER:
                            duplicates = 0
                            resend = False
                            if self.timeout > 0.1:
                                self.timeout -= 0.1
                                self.simulator.sndr_socket.settimeout(self.timeout)
                            break
                        # general error -> resend
                        else:
                            self.simulator.u_send(send_array)
                    # package was corrupt -> resend
                    else:
                        self.simulator.u_send(send_array)
                        duplicates += 1
                        if duplicates == 3 and sent:
                            self.timeout *= 2
                            self.simulator.sndr_socket.settimeout(self.timeout)
                            duplicates = 0
                            # prevent infinite loop
                            if self.timeout > 10:
                                sys.exit()
            # socket timeout -> resend
            except socket.timeout:
                resend = True
                self.simulator.u_send(send_array)
                duplicates += 1
                if duplicates >= 3:
                    duplicates = 0
                    self.timeout *= 2
                    if self.timeout > 10:
                        sys.exit()
                    self.simulator.sndr_socket.settimeout(self.timeout)


if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    # sndr = BogoSender()
    # sndr.send(DATA)
    # use OurSender
    sndr = OurSender()
    sndr.send(DATA)

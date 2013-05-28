#!/usr/bin/env python
#
# scopes.py
#
# This code choses the commands to send
#
# Author P G Jones - 28/05/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import re
import numpy

class Tektronix(object):
    """ Communication with a tektronix scope."""
    def __init__(self, connection):
        """ Initialise with a connection instance."""
        self._connection = connection
        self._connection.send("lock none") # Unlock
        self._connection.send("acq:state off")
        self._connection.send("*OPC?") # Will wait until scope is ready
    def __del__(self):
        """ Free up the scope."""
        self._connection.send("lock none") # Unlock
    def interactive(self):
        """ Control the scope interactively."""
        print "Enter: Interactive mode."
        try:
            while True:
                command = raw_input("COMMAND: ")
                print self._connection.ask(command), "\n"
        except KeyboardInterrupt:
            print "Exit: Interative mode."
    def get_active_channels(self):
        """ Return the number of interactive channels."""
        self._connection.send("header on")
        self._connection.send("verbose 1")
        channels = {}
        for select in self._connection.ask("select?").strip()[8:].split(';'):
            channel_info = re.match("CH(\d) (\d)", select)
            if channel_info is not None:
                channel = int(channel_info.groups()[0])
                state = channel_info.groups()[1]  == '1'
                channels[channel] = state
        return channels
    def get_waveform(self, channel):
        """ Acquire a waveform from channel=channel."""
        self._connection.send("header off")
        self._connection.send("verbose 0")
        self._connection.send("wfmpre:pt_fmt y") # Single point format
        self._connection.send("data:source ch%i" % channel)
        self._data_type = '>' + 'i' + '1'
        data = self._connection.ask("curve?")
        header_len = 2 + int(data[1])
        waveform = numpy.fromstring(data[header_len:], self._data_type)
        return waveform

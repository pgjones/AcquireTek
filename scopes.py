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
        self._connection.send("verbose 1") # If the headers are on ensure they are verbose
        self._locked = False # Needs to be locked to acquire waveforms
        self._preamble = {}
        self._channels = {}
    def __del__(self):
        """ Free up the scope."""
        self._connection.send("lock none") # Unlock
    def interactive(self):
        """ Control the scope interactively."""
        if self._locked:
            raise Exception("Scope is locked.")
        print "Enter: Interactive mode."
        try:
            while True:
                command = raw_input("COMMAND: ")
                print self._connection.ask(command), "\n"
        except KeyboardInterrupt:
            print "Exit: Interative mode."
    def get_active_channels(self):
        """ Return the number of interactive channels."""
        if not self._locked:
            self._find_active_channels()
        return self._channels
    def lock(self):
        """ Get the current settings and allow no more changes."""
        self._connection.send("header off")
        self._connection.send("wfmpre:pt_fmt y") # Single point format
        self._find_active_channels()
        for channel in self._channels.keys():
            if self._channels[channel]:
                self._get_preamble(channel)
        self._locked = True
    def unlock(self):
        """ Unlock and allow changes."""
        self._locked = False
    def get_waveform(self, channel):
        """ Acquire a waveform from channel=channel."""
        if self._locked == False:
            raise Exception("Not locked.")
        self._connection.send("data:source ch%i" % channel)
        data = self._connection.ask("curve?")
        header_len = 2 + int(data[1])
        waveform = numpy.fromstring(data[header_len:], self._data_type)
        # Now convert the waveform into voltage units
        waveform = self._preamble[channel]['YZERO'] + (waveform - self._preamble[channel]['YOFF']) * self._preamble[channel]['YMULT']
        # Now build the relevant timing array
        timeform = self._preamble[channel]['XZERO'] + (numpy.arange(self._preamble[channel]['NR_PT']) - self._preamble[channel]['PT_OFF']) * \
            self._preamble[channel]['XINCR']
        return (timeform, waveform)
#################################################################################################### 
    def _find_active_channels(self):
        """ Finds out how many channels are active."""
        self._connection.send("header on")
        for select in self._connection.ask("select?").strip()[8:].split(';'):
            channel_info = re.match("CH(\d) (\d)", select)
            if channel_info is not None:
                channel = int(channel_info.groups()[0])
                state = channel_info.groups()[1]  == '1'
                self._channels[channel] = state
        self._connection.send("header off")
    def _get_preamble(self, channel):
        """ Get the waveform data type preamble."""
        preamble_fields = {'BYT_NR' : int, # data width for waveform
                           'BIT_NR' : int, # number of bits per waveform point
                           'ENCDG'  : str, # encoding of waveform (binary/ascii)
                           'BN_FMT' : str, # binary format of waveform
                           'BYT_OR' : str, # ordering of waveform data bytes (LSB/MSB)
                           'WFID'   : str, # Description of the data
                           'NR_PT'  : int, # record length of record waveform
                           'PT_FMT' : str, # Point format (Y/ENV)
                           'XUNIT'  : str,
                           'XINCR'  : float,
                           'XZERO'  : float,
                           'PT_OFF' : int,
                           'YUNIT'  : str,
                           'YMULT'  : float,
                           'YOFF'   : float,
                           'YZERO'  : float,
                           'VSCALE' : float, 
                           'HSCALE' : float, 
                           'VPOS'   : float,
                           'VOFFSET': float,
                           'HDELAY' : float,
                           'COMPOSITION': str,
                           'FILTERFREQ' : int }
        self._connection.send("header on")
        self._connection.send("data:source ch%i" % channel)
        preamble = {}
        for preamble_setting in self._connection.ask("wfmpre?").strip()[8:].split(';'):
            key, value = preamble_setting.split(' ',1)
            preamble[key] = preamble_fields[key](value) # Conver the value to the correct field type 
        self._preamble[channel] = preamble
        self._connection.send("header off")
        # Now set the data type
        if self._preamble[channel]['BYT_OR'] == 'MSB':
            self._data_type = '>'
        else:
            self._data_type = '<'
        if self._preamble[channel]['BN_FMT'] == 'RI':
            self._data_type += 'i'
        else:
            self._data_type += 'u'
        self._data_type += str(self._preamble[channel]['BYT_NR'])

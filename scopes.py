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
import time

class Tektronix(object):
    """ Base class for tektronix scopes."""
    _preamble_fields = {'BYT_NR' : int, # data width for waveform
                        'BIT_NR' : int, # number of bits per waveform point
                        'ENCDG'  : str, # encoding of waveform (binary/ascii)
                        'BN_FMT' : str, # binary format of waveform
                        'BYT_OR' : str, # ordering of waveform data bytes (LSB/MSB)
                        'NR_PT'  : int, # record length of record waveform
                        'PT_FMT' : str, # Point format (Y/ENV)
                        'XUNIT'  : str, # X unit 
                        'XINCR'  : float, # Difference between two x points
                        'XZERO'  : float, # X zero value
                        'PT_OFF' : int, # Ignored?
                        'YUNIT'  : str, # Y unit
                        'YMULT'  : float, # Difference between two y point
                        'YOFF'   : float, # Y offset
                        'YZERO'  : float, # Y zero value
                        'RECORDLENGTH' : int } # Number of data points
    def __init__(self, connection):
        """ Initialise the scope with a connection to the scope."""
        # Initiliase setttings to nothing
        self._preamble = {}
        self._channels = {} 
        self._connection = connection
        self._connection.send_sync("*rst") # Reset the scope
        self._connection.send_sync("lock none") # Unlock the front panel
        self._connection.send_sync("*cls") # Clear the scope
        self._connection.send_sync("verbose 1") # If the headers are on ensure they are verbose
        self._locked = False # Local locking of scope settings
        self._data_start = 1
        self._triggered = False
    def __del__(self):
        """ Free up the scope."""
        self.unlock()
#################################################################################################### 
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
        """ Return the number of active channels."""
        if not self._locked:
            self._find_active_channels()
        return self._channels
    def lock(self):
        """ Get the current settings and allow no more changes."""
        self._connection.send_sync("lock all") # Prevent people channing the settings via the front panel
        self._connection.send_sync("header off") # Turn all headers off
        self._locked = True
    def begin(self):
        """ Start taking data."""
        if self._locked is False:
            print "Not locked"
            raise
        time.sleep(10) # Prudent to wait for the scope to recover from the settings...
        self._find_active_channels()
        for channel in self._channels.keys():
            if self._channels[channel]:
                self._get_preamble(channel)
        self._connection.send_sync("message:show 'Taking Data, scope is locked.'")
        self._connection.send_sync("message:state on")
    def unlock(self):
        """ Unlock and allow changes."""
        self._locked = False
        self._connection.send_sync("message:state off")
        self._connection.send_sync("lock none") # Allow the front panel to be used
    def get_preamble(self, channel):
        return self._preamble[channel]
#### General Settings ###############################################################################
    def set_display_x(self, scale, pos=0):
        """ The scope x display settings, these do not affect the waveform.
        scale in seconds per div and pos in percentage of screen."""
        self._connection.send_sync("horizontal:scale %f" % scale)
        self._connection.send_sync("horizontal:position %i" % pos)
    def set_display_y(self, channel, mult, pos=0.0, offset=0.0):
        """ The channel y display settings, these do not affect the waveform.
        mult or volts per div, yoffset (in volts) and position in divs."""
        self._connection.send_sync("ch%i:volts %f" %(channel, mult))
        self._connection.send_sync("ch%i:position %f" %(channel, pos))
        self._connection.send_sync("ch%i:offset %f" %(channel, offset))
#### Waveform Settings ##############################################################################
    def set_data_mode(self, data_start=1, data_stop=None):
        """ Set the settings for the data returned by the scope."""
        self._connection.send_sync("wfmoutpre:pt_fmt y") # Single point format
        self._connection.send_sync("data:encdg ribinary") # Signed int binary mode
        self._connection.send_sync("data:start %i" % data_start) # Start point
        self._data_start = data_start
        if data_stop is None:
            data_stop = int(self._connection.ask("horizontal:acqlength?"))
        self._connection.send_sync("data:stop %i" % data_stop) # 100000 is full 
#### Channel Settings ###############################################################################
    def set_channel_y(self, channel, scale):
        self._connection.send_sync("ch%i:scale %f" % (channel, scale))
    def set_active_channel(self, channel, active=True):
        if active:
            self._connection.send_sync("select:ch%i on" % channel)
        else:
            self._connection.send_sync("select:ch%i off" % channel)
    def set_invert_channel(self, channel, invert=True):
        """ Invert the channel."""
        if invert:
            self._connection.send_sync("ch%i:invert on" % channel)
        else:
            self._connection.send_sync("ch%i:invert off" % channel)
    def set_channel_coupling(self, channel, coupling="ac"):
        self._connection.send_sync("ch%i:coupling %s" % (channel, coupling))
#### Acquisition Type ###############################################################################
    def set_single_acquisition(self):
        """ Set the scope in single acquisition mode."""
        self._connection.send_sync("acquire:mode sample") # Single acquisition mode, not average
    def set_average_acquisition(self, averages):
        """ Set the scope in average acquisition mode."""
        self._connection.send_sync("acquire:mode average")
        self._connection.send_sync("acquire::numavg %i" % averages)
#### Trigger Settings ###############################################################################
    def set_untriggered(self):
        """ Set the scope to untriggered mode."""
        self._triggered = False
        self._connection.send_sync("trigger:a:mode auto")
    def set_edge_trigger(self, trigger_level, channel, falling=False):
        """ Set an edge trigger with the settings."""
        self._triggered = True
        self._connection.send_sync("trigger:a:type edge") # Chose the edge trigger
        self._connection.send_sync("trigger:a:mode normal") # Normal mode (waits for a trigger)
        self._connection.send_sync("trigger:a:edge:source ch%i" % channel)
        self._connection.send_sync("trigger:a:edge:coupling dc") # DC coupling
        if falling:
            self._connection.send_sync("trigger:a:edge:slope fall") # Falling or ...
        else:
            self._connection.send_sync("trigger:a:edge:slope rise") # ... rising slope
        self._connection.send_sync("trigger:a:level %f" % trigger_level) # Sets the trigger level in Volts
        self._connection.send_sync("trigger:a:level:ch%i %f" % (channel, trigger_level)) # Sets the trigger level in Volts
    def get_trigger_frequency(self):
        trigger_frequency = self._connection.ask("trigger:frequency?")
        if trigger_freqeuncy == 9.9100e+37:
            return 0.0
        else:
            return trigger_frequency
#### Data acquistion ################################################################################
    def acquire(self):
        """ Wait until scope has an acquisition."""
        self._connection.send("acquire:state run") # Equivalent to on
        # Wait until acquiring and there is a trigger
        while True:
            acquisition_state = self._connection.ask("acquire:state?")
            if acquisition_state is not None and int(acquisition_state) != 0: # acquired a trigger
                if self._triggered and self._connection.ask("trigger:state?") != "READY": # Triggered as well 
                    break
                elif not self._triggered:
                    break
                # Otherwise carry on
    def get_waveform(self, channel):
        """ Acquire a waveform from channel=channel."""
        if self._locked == False or self._channels[channel] == False:
            raise Exception("Not locked or channel not active.")
        self._connection.send("data:source ch%i" % channel) # Set the data source to the channel
        data = self._connection.ask("curve?") # Ask for the data
        if data is None:
            self._connection.ask("*opc?") # Wait until scope is ready
            raise Exception("Scope has errored.")
        header_len = 2 + int(data[1])
        waveform = numpy.fromstring(data[header_len:], self._get_data_type(channel))
        # Now convert the waveform into voltage units
        waveform = self._preamble[channel]['YZERO'] + (waveform - self._preamble[channel]['YOFF']) * self._preamble[channel]['YMULT']
        return waveform
    def get_timeform(self, channel):
        """ Return the timebase for the waveform."""
        # Now build the relevant timing array correcting for data portion acquired
        timeform = self._preamble[channel]['XZERO'] + self._data_start * self._preamble[channel]['XINCR'] + \
            (numpy.arange(self._preamble[channel]['NR_PT']) - self._preamble[channel]['PT_OFF']) * self._preamble[channel]['XINCR']
        return timeform
#### Internal ###################################################################################### 
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
        """ Retrieve the preamble from the scope."""
        self._connection.send_sync("data:source ch%i" % channel) # Set the data source to the channel
        self._connection.send_sync("header on") # Turn headers on
        preamble = {}
        for preamble_setting in self._connection.ask("wfmoutpre?").strip()[len("wfmoutpre:") + 1:].split(';'): # Ask for waveform information
            key, value = preamble_setting.split(' ',1)
            if key in Tektronix._preamble_fields.keys():
                preamble[key] = Tektronix._preamble_fields[key](value) # Conver the value to the correct field type 
            else:
                print "Preamble key", key, "is ignored."
        self._preamble[channel] = preamble
        self._connection.send_sync("header off") # Turn the headers offf
    def _get_data_type(self, channel):
        """ Return the data type for the given channel."""
        data_type = ""
        if self._preamble[channel]['BYT_OR'] == 'MSB': # Endeaness
            data_type = '>'
        else:
            data_type = '<'
        if self._preamble[channel]['BN_FMT'] == 'RI': # Signed or unsigned
            data_type += 'i'
        else:
            data_type += 'u'
        data_type += str(self._preamble[channel]['BYT_NR']) # Number of bits per data point
        return data_type
                        
class Tektronix2000(Tektronix):
    """ Specific commands for the DPO/MSO 2000 series scopes."""
    # Update the preamble fields with those specific to this scope model                    
    Tektronix._preamble_fields.update( { 'WFID'   : str, # Description of the data
                                         'VSCALE' : float, 
                                         'HSCALE' : float, 
                                         'VPOS'   : float,
                                         'VOFFSET': float,
                                         'HDELAY' : float,
                                         'COMPOSITION': str,
                                         'FILTERFREQ' : int } )
    def __init__(self, connection):
        """ Intialise the scope with a connection."""
        super(Tektronix2000, self).__init__(connection)

class Tektronix3000(Tektronix):
    """ Specific commands for the DPO/MSO 2000 series scopes."""
    # Update the preamble fields with those specific to this scope model                    
    Tektronix._preamble_fields.update( { 'CENTERFREQUENCY' : float,
                                         'DOMAIN'          : str, 
                                         'REFLEVEL'        : float,
                                         'SPAN'            : float,
                                         'WFMTYPE'         : str } )
    def __init__(self, connection):
        """ Intialise the scope with a connection."""
        super(Tektronix3000, self).__init__(connection)

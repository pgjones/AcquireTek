#!/usr/bin/env python
#
# scope_connections.py
#
# This code opens the connection to send and recieve from a scope
#
# Author P G Jones - 28/05/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
from pyvisa.vpp43 import visa_library, visa_exceptions
visa_library.load_library("/Library/Frameworks/Visa.framework/VISA") # Mac specific??
import visa

class VisaUSB(object):
    """ Connect via visa/usb."""
    def __init__(self):
        """ Try the default connection."""
        for instrument in visa.get_instruments_list():
            if instrument[0:3] == "USB":
                self._connection = visa.instrument(instrument)
                print "Connecting to", instrument
                print "Which has identity:", self.ask("*idn?") # Ask the scope for its identity
    def send(self, command):
        """ Send a command, doesn't expect a returned result."""
        self._connection.write(command)
    def ask(self, command):
        """ Send a command and expect an answer."""
        try:
            return self._connection.ask(command)
        except visa_exceptions.VisaIOError:
            # No answer given
            return None

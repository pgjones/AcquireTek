#!/usr/bin/env python
#
# scope_connections.py
#
# This code opens the connection to send and recieve from a scope
#
# Author P G Jones - 28/05/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
try:
    from pyvisa.vpp43 import visa_library, visa_exceptions
    visa_library.load_library("/Library/Frameworks/Visa.framework/VISA") # Mac specific??
    import visa
except ImportError:
    print "No VISA/pyVISA software installed, cannot use VisaUSB"

import socket

class VisaUSB(object):
    """ Connect via visa/usb."""
    def __init__(self):
        """ Try the default connection."""
        try:
            for instrument in visa.get_instruments_list():
                if instrument[0:3] == "USB":
                    self._connection = visa.instrument(instrument)
                    print "Connecting to", instrument
                    print "Which has identity:", self.ask("*idn?") # Ask the scope for its identity
        except visa_exceptions.VisaIOError:
            print "Cannot connect to any instrument."
            raise
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
        except pyvisa.visa_exceptions.VisaIOError:
            return None

class TCPIP(object):
    """ Connect via TCP/IP i.e. ethernet."""
    def __init__(self, ip, port):
        """ Connect with the ip and port address."""
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((ip, port))
        self._connection.setblocking(False)
        print "Connecting to %s:%i" % (ip, port)
        print "Which had identity:", self.ask("*idn?")
    def __del__(self):
        """ Close the connection."""
        self._connection.close()
    def send(self, command):
        """ Send a command, doesn't expect a returned result."""
        self._connection.send(command)

    def ask(self, command):
        """ Send a command and expect an answer."""
        self._connection.send(command)
        response = ''
        while True:
            char = ""
            try:
                char = self._connection.recv(1)
            except:
                if response.rstrip() != "":
                    break
            if char:
                response += char
        return response.rstrip()

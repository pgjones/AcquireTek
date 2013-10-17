#!/usr/bin/env python
#
# scope_connections.py
#
# This code opens the connection to send and recieve from a scope
#
# Author P G Jones - 28/05/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import logging
logger = logging.getLogger(__name__)

try:
    from pyvisa.vpp43 import visa_library, visa_exceptions
    visa_library.load_library("/Library/Frameworks/Visa.framework/VISA") # Mac specific??
    import visa
except ImportError:
    print "No VISA/pyVISA software installed, cannot use VisaUSB"

import socket

class TekConnection(object):
    """ Base class for Tektronix scope connections."""
    def __init__(self):
        print "\n-----------------------------------------------------------------------------------"
    def __del__(self):
        print "-----------------------------------------------------------------------------------\n"
    def sync(self):
        """ Send the *OPC command, and wait until scope is ready for more data."""
        self.send("*wai")
    def identity(self):
        """ Return the identity and connection method."""
        return self.ask("*idn?")
    def send_sync(self, command):
        """ Send a command and wait till the scope is ready."""
        self.send(command)
        self.sync()
    def send(self, command):
        logging.debug("send: %s" % command)
        self._send(command)
    def ask(self, command):
        logging.debug("ask: %s" % command)
        response = self._ask(command)
        logging.debug("response: %s" % response)
        return response
    def _send(self, command):
        pass
    def _ask(self, command):
        pass

class VisaUSB(TekConnection):
    """ Connect via visa/usb."""
    def __init__(self):
        """ Try the default connection."""
        super(VisaUSB, self).__init__()
        try:
            for instrument in visa.get_instruments_list():
                if instrument[0:3] == "USB":
                    self._connection = visa.instrument(instrument, send_end=True)
                    print "Connecting to", instrument
                    print "Scope identity:", self.identity()
        except visa_exceptions.VisaIOError:
            logging.exception("Cannot connect to any instrument.")
            print "Cannot connect to any instrument."
            raise
    def _send(self, command):
        """ Send a command, doesn't expect a returned result."""
        try:
            self._connection.write(command)
        except visa_exceptions.VisaIOError:
            logging.exception("send")
            print "VisaUSB::send: Issues."
    def _ask(self, command):
        """ Send a command and expect an answer."""
        try:
            return self._connection.ask(command)
        except visa_exceptions.VisaIOError:
            logging.exception("ask")
            # No answer given
            print "VisaUSB::ask: Issues."
            return None

class TCPIP(TekConnection):
    """ Connect via TCP/IP i.e. ethernet."""
    def __init__(self, ip, port):
        """ Connect with the ip and port address."""
        super(VisaUSB, self).__init__()
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection.connect((ip, port))
        self._connection.setblocking(False)
        print "Connecting to %s:%i" % (ip, port)
        print "Scope identity:", self.identity()
    def __del__(self):
        """ Close the connection."""
        self._connection.close()
    def _send(self, command):
        """ Send a command, doesn't expect a returned result."""
        self._connection.send(command)

    def _ask(self, command):
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
    

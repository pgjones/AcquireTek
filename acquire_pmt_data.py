#!/usr/bin/env python
#
# acquire_pmt_signals.py
#
# Acquisition of PMT Data from a Tektronix scope with saving of the signal to root file.
#
# Author P G Jones - 05/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import scope_connections
import scopes
import utils
import time
import sys

usb_conn = scope_connections.VisaUSB()
tek_scope = scopes.Tektronix2000(usb_conn)
# First setup the scope, lock the front panel
tek_scope.lock()
tek_scope.set_single_acquisition() # Single signal acquisition mode
tek_scope.set_invert_channel(1, True) # Invert both channels
tek_scope.set_invert_channel(2, True) # Invert both channels
trigger = -0.04 # Volts
tek_scope.set_edge_trigger(trigger, 2, True) # Falling edge trigger
tek_scope.set_data_mode(49500, 50500)
tek_scope.lock() # Re acquires the preamble
# Now create a root file to save 2 channel data in
results = utils.File("results.pkl", 2)

t_start = time.time()
acquire_time = int(sys.argv[1]) * 60 # in seconds
print "Started at", t_start
while time.time() - t_start < acquire_time:
    tek_scope.acquire(True) # Wait for triggered acquisition
    try:
        results.set_data(tek_scope.get_waveform(1), 1)
        results.set_data(tek_scope.get_waveform(2), 2)
        results.save()
    except Exception, e:
        print "Scope died, acquisition lost."
        print e
    print "Time left:", acquire_time - (time.time() - t_start), "s"
tek_scope.unlock()
results.close()

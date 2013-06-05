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
import root_utils
import time

usb_conn = scope_connections.VisaUSB()
tek_scope = scopes.Tektronix2000(usb_conn)
# First setup the scope, lock the front panel
tek_scope.lock()
tek_scope.set_single_acquisition() # Single signal acquisition mode
tek_scope.set_invert_channel(1, True) # Invert both channels
tek_scope.set_invert_channel(2, True) # Invert both channels
trigger = 0.03 # Volts
tek_scope.set_edge_trigger(trigger, 1)
tek_scope.set_data_mode(49500, 50500)
tek_scope.lock() # Re acquires the preamble
# Now create a root file to save 2 channel data in
results = root_utils.ValueFile("results.root", 2)

t_start = time.time()
acquire_time = 30 * 60 # in seconds
print "Started at", t_start
while time.time() - t_start < acquire_time:
    tek_scope.acquire(True) # Wait for triggered acquisition
    try:
        # Channel 1
        hist_1 = root_utils.waveform_to_hist(tek_scope.get_waveform(1), tek_scope.get_waveform_units(1))
        results.set_data(root_utils.integrate_signal(hist_1, trigger), 1)
        # Channel 2
        hist_2 = root_utils.waveform_to_hist(tek_scope.get_waveform(2), tek_scope.get_waveform_units(2))
        results.set_data(root_utils.integrate_signal(hist_2, trigger), 2)
        results.save()
    except Exception:
        print "Scope died, acquisition lost."
    print "Time left:", acquire_time - (time.time() - t_start), "s"
tek_scope.unlock()

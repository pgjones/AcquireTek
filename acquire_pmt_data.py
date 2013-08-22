#!/usr/bin/env python
#
# acquire_pmt_signals.py
#
# Acquisition of PMT Data from a Tektronix scope with saving of the signal to root file.
#
# Author P G Jones - 05/06/2013 <p.g.jones@qmul.ac.uk> : First revision
################################################################################## 
import scope_connections
import scopes
import utils
import time
import sys
import os
import shutil
import datetime
from pyvisa.vpp43 import visa_exceptions

duration=int(sys.argv[1])
if duration > 60:
    interval=60 * 60
else:
    interval=duration * 60
milestone=interval
kind=sys.argv[3]
today=str(datetime.date.today())

usb_conn = scope_connections.VisaUSB()
tek_scope = scopes.Tektronix2000(usb_conn)
# First setup the scope, lock the front panel
tek_scope.lock()
tek_scope.set_single_acquisition() # Single signal acquisition mode
tek_scope.set_invert_channel(1, True) # Invert both channels
tek_scope.set_invert_channel(2, True) # Invert both channels
count=1
name='%s_%d_hour_%s' %(today,duration/60,kind)
roll=os.walk('results').next()[1]
for i in roll:
    if i==name:
        name='%s_%d_hour_%s_%d' %(today,duration/60,kind,count)
        for i in roll:
            if i==name:
                count+=1
                i=roll[0]
os.chdir('results')
print "Saving to", name
os.mkdir(name)
os.chdir(name)

trigger = -0.004 # Volts
trigger_channel = 2
ymult = 100e-3 # Volts
tek_scope.set_edge_trigger(trigger, trigger_channel, True) # Falling edge trigger
tek_scope.set_channel_coupling(1, "ac")
tek_scope.set_channel_coupling(2, "ac")
tek_scope.set_channel_y(1, ymult)
tek_scope.set_channel_y(2, ymult)
tek_scope.set_data_mode(49500, 50500)
tek_scope.lock() # Re acquires the preamble
# Now create a root file to save 2 channel data in
results = utils.HDF5File("results", 2)
results.set_meta_data("trigger", trigger)
results.set_meta_data("trigger_channel", trigger_channel)
results.set_meta_data("channel_y_mult", ymult)
results.set_meta_data("timeform_1", tek_scope.get_timeform(1))
results.set_meta_data("timeform_2", tek_scope.get_timeform(2))
results.set_meta_data("ch1", tek_scope._get_preamble(1))
results.set_meta_data("ch2", tek_scope._get_preamble(2))

print "Waiting", sys.argv[2], "seconds to record", duration, " minutes in", interval, "second files"
time.sleep(float(sys.argv[2])*60)

t_start = time.time()
acquire_time = duration * 60 # in seconds
print "Started at", datetime.datetime.now().time()

filecount=0
while time.time()-t_start<acquire_time:
    filecount+=1
    # Now create a root file to save 2 channel data in
    _file=name+"_results"+str(filecount)
    results = utils.HDF5File(_file, 2)
    results.set_meta_data("timeform_1", tek_scope.get_timeform(1))
    results.set_meta_data("timeform_2", tek_scope.get_timeform(2))
    #results.set_meta_dict(tek_scope.get_preamble())
    while time.time()-t_start<=milestone:
        tek_scope.acquire(True) # Wait for triggered acquisition
        try:
            results.add_data(tek_scope.get_waveform(1), 1)
            results.add_data(tek_scope.get_waveform(2), 2)
        except Exception, e:
            print "Scope died, acquisition lost."
            print e
        except visa_exceptions.VisaIOError, e:
            print "Serious death"
            time.wait(1)
        print "Time left:", acquire_time - (time.time() - t_start), "s"
    print "New file at", time.time()-t_start
    milestone+=interval

    results.save()
    results.close()

tek_scope.unlock()

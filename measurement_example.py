#!/usr/bin/env python
#
# measurement_example.py
#
# Acquisition of single triggerred measurement data from a Tektronix scope.
# Data is saved to a hdf5 file.
#
# Author P G Jones - 2013-10-23 <p.g.jones@qmul.ac.uk> : First revision
################################################################################## 
import optparse
import scopes
import scope_connections
import utils
import datetime
import time
from pyvisa.vpp43 import visa_exceptions

def measurement_example(name, n_events, trigger, trigger_channel, y_scale, cursor_low, cursor_high):
    """ Acquire a set of measurements for a triggerred single acquisition on one channel."""
    tek_scope = scopes.Tektronix2000(scope_connections.VisaUSB())
    # First setup the scope, lock the front panel
    tek_scope.lock()
    tek_scope.set_active_channel(1)
    tek_scope.set_single_acquisition() # Single signal acquisition mode
    tek_scope.set_channel_y(1, y_scale)
    tek_scope.set_edge_trigger(trigger, trigger_channel, True) # Falling edge trigger
    tek_scope.set_horizontal_scale(1e-8)
    tek_scope.set_cursors(cursor_low, cursor_high)
    tek_scope.set_measurement("area")
    tek_scope.begin()

    file_name = name + "_" + str(datetime.date.today())
    results = utils.HDF5File(file_name, 1)
    results.add_meta_data("trigger", trigger)
    results.add_meta_data("trigger_channel", trigger_channel)
    results.add_meta_data("cursor_low", cursor_low)
    results.add_meta_data("cursor_high", cursor_high)
    results.add_meta_data("y_scale", y_scale)

    last_save_time = datetime.datetime.now()
    print "Starting data taking at time", last_save_time.strftime("%Y-%m-%d %H:%M:%S")
    for event in range(0, n_events):
        tek_scope.acquire()
        try:
            print tek_scope.get_measurement(1)
            results.add_data(tek_scope.get_measurement(1), 1)
        except visa_exceptions.VisaIOError, e:
            print "Serious death", e
            time.sleep(10)
        except Exception, e:
            print "Scope died, acquisition lost.", e
            time.sleep(10)
        if datetime.datetime.now() - last_save_time > datetime.timedelta(seconds=60):
            results.autosave()
            last_save_time = time.time()
    results.save()
    print "Finished at", time.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog name n_events", version="%prog 1.0")
    parser.add_option("-c", type="int", dest="channel", help="Trigger channel", default=1)
    parser.add_option("-t", type="float", dest="trigger", help="Trigger level", default=-0.004)
    parser.add_option("-y", type="float", dest="y_scale", help="Y Scaling", default=100e-3)
    parser.add_option("-a", type="float", dest="cursor_low", help="Cursor low (integral low bound)", default=-10e-9)
    parser.add_option("-b", type="float", dest="cursor_high", help="Cursor high (integral high bound)", default=10e-9)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print "Incorrect number of arguments"
        parser.print_help()
        exit(0)
    measurement_example(args[0], int(args[1]), options.trigger, options.channel, options.y_scale, options.cursor_low, options.cursor_high)

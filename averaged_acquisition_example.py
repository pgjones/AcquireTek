#!/usr/bin/env python
#
# averaged_acquisition_example.py
#
# Acquisition of average untriggered waveform data from a Tektronix scope.
# Data is saved to a hdf5 file.
#
# Author P G Jones - 2013-09-16 <p.g.jones@qmul.ac.uk> : First revision
################################################################################## 
import optparse
import scopes
import scope_connections
import utils
import datetime
from pyvisa.vpp43 import visa_exceptions

def averaged_acquisition_example(name, n_events, averages):
    """ Acquire a set of triggerred single acquisitions for two channels."""
    tek_scope = scopes.Tektronix2000(scope_connections.VisaUSB())
    # First setup the scope, lock the front panel
    tek_scope.lock()
    tek_scope.set_active_channel(1)
    tek_scope.set_active_channel(2)
    tek_scope.set_average_acquisition(averages)
    tek_scope.set_data_mode(49500, 50500)
    tek_scope.lock() # Re acquires the preamble
    # Now create a HDF5 file and save the meta information
    file_name = name + "_" + str(datetime.date.today())
    results = utils.HDF5File(file_name, 2)
    results.add_meta_data("ch1_timeform", tek_scope.get_timeform(1))
    results.add_meta_data("ch2_timeform", tek_scope.get_timeform(2))
    results.add_meta_dict(tek_scope.get_preamble(1), "ch1")
    results.add_meta_dict(tek_scope.get_preamble(2), "ch2")

    last_save_time = datetime.datetime.now()
    print "Starting data taking at time", last_save_time.strftime("%Y-%m-%d %H:%M:%S")
    for event in range(0, n_events):
        tek_scope.acquire()
        try:
            results.add_data(tek_scope.get_waveform(1), 1)
            results.add_data(tek_scope.get_waveform(2), 2)
        except Exception, e:
            print "Scope died, acquisition lost."
            print e
        except visa_exceptions.VisaIOError, e:
            print "Serious death"
            time.wait(1)
        if datetime.datetime.now() - last_save_time > datetime.timedelta(seconds=60):
            results.autosave()
            last_save_time = time.time()
    results.save()
    print "Finished at", time.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    parser = optparse.OptionParser(usage = "usage: %prog name n_events", version="%prog 1.0")
    parser.add_option("-a", type="int", dest="averages", help="Averages", default=2)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print "Incorrect number of arguments"
        parser.print_help()
        exit(0)
    averaged_acquisition_example(args[0], int(args[1]), options.averages)

#!/usr/bin/env python
#
# utils.py
#
# Utility functions to integrate and save waveforms in pickle format.
#
# Author P G Jones - 06/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import numpy
import pickle

def integrate_signal(data_forms, trigger=0.0):
    """ Return the integrals of any pulses above the trigger."""
    integrals = []
    for bin in range(0, len(data_forms[1])):
        if data_forms[1][bin] > trigger:
            integral = 0.0
            # First go back and find early integral
            for pre_bin in range(bin, -1):
                if data_forms[1][pre_bin] <= trigger / 2.0:
                    break
                integral += data_forms[1][pre_bin]
            # Now go forwards and find full integral
            for post_bin in range(bin, len(data_forms[1])):
                if data_forms[1][post_bin] <= trigger / 2.0:
                    bin = post_bin # Start from here for next search
                    break
                integral += data_forms[1][post_bin]
            integrals.append(integral)
    return integrals

class File(object):
    """ A pickle file."""
    def __init__(self, file_path, channels):
        """ Initialise saving the path and setting up a dict."""
        self._file_path = file_path
        self._data = {}
        for channel in range(1, channels + 1):
            self._data[channel] = []
    def set_data(self, data, channel):
        """ Add a data point."""
        self._data[channel].append(data)
    def close(self):
        """ Close the file, write the data."""
        with open(self._file_path, "wb") as file_:
            pickle.dump(self._data, file_)
    def save(self):
        """ Intermediate save of the data."""
        pass

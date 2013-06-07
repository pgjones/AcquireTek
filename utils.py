#!/usr/bin/env python
#
# utils.py
#
# Utility functions to save waveforms in pickle format.
#
# Author P G Jones - 06/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import pickle

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

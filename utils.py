#!/usr/bin/env python
#
# utils.py
#
# Utility functions to save waveforms in various formats.
#
# Author P G Jones - 06/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import re

class File(object):
    """ Generic file, no saving."""
    def __init__(self, file_path, channels):
        """ Intialise the data structure."""
        self._file_path = file_path
        self._data = {} # Dict by channel or list of waveforms
        for channel in range(1, channels + 1):
            self._data[channel] = []
        self._meta_data = {} # Meta data dict
    def set_meta_dict(self, dict):
        """ Set the meta data for a whole dict."""
        for key in dict.keys():
            self._meta_data[key] = dict[key]
    def set_meta_data(self, key, data):
        """ Set the meta data for key."""
        self._meta_data[key] = data
    def add_data(self, data, channel):
        """ Add data for the channel."""
        self._data[channel].append(data)
    def get_meta_data(self, key):
        """ Get the meta data for key."""
        return self._meta_data[key]
    def get_data(self, channel):
        """ Get the data for channel."""
        return self._data[channel]
#--- To Override -----------------------------------------------------------------------------------
    def close(self):
        """ Close/finish."""
        pass
    def save(self):
        """ Save the data to a file."""
        pass
    def load(self):
        """ Load the data from a file."""

#### Pickle ######################################################################################## 
import pickle

class PickleFile(File):
    """ A pickle file."""
    def __init__(self, file_path, channels):
        """ Initialise a pickle file."""
        super(PickleFile, self).__init__(file_path, channels)
        self._file_path += ".pkl"
    def save(self):
        """ Save of the data to a pickle file."""
        full_data = { "meta" : self._meta_data,
                      "data" : self._data }
        with open(self._file_path, "wb") as file_:
            pickle.dump(full_data, file_)
    def load(self):
        """ Load the data from a pickle file."""
        with open(self._file_path, "rb") as file_:
            full_data = pickle.load(file_)
        self._meta_data = full_data["meta"]
        self._data = full_data["data"]

#### h5py ########################################################################################## 
try:
    import h5py
except ImportError:
    pass # No hdf5 files for you!

class HDF5File(File):
    """ A hdf5 file."""
    def __init__(self, file_path, channels):
        """ Initialise a hdf5 file."""
        super(HDF5File, self).__init__(file_path, channels)
        self._file_path += ".hdf5"
    def save(self):
        """ Save of the data to a hdf5 file."""
        with h5py.File(self._file_path, "w") as file_:
            for key in self._meta_data.keys():
                file_.attrs[key] = self._meta_data[key]
            for channel in self._data.keys():
                data = self._data[channel]
                for index, waveform in enumerate(data):
                    file_.create_dataset("ch%i_%i" % (channel, index), data=waveform)                
    def load(self):
        """ Load the data from a hdf5 file."""
        with h5py.File(self._file_path, "r") as file_:
            for key in file_.attrs:
                self._meta_data[key] = file_.attrs[key]
            for dataset in file_:
                channel_info = re.match("ch(\d)_(\d)", dataset)
                channel = int(channel_info.groups()[0])
                waveform = int(channel_info.groups()[1])
                self._data[channel].append(file_[dataset].value)

#### root ########################################################################################## 
try:
    import ROOT
except ImportError:
    pass # No root files for you!

class RootFile(File):
    """ A root file."""
    def __init__(self, file_path, channels):
        """ Initialise a root file."""
        super(ROOTFile, self).__init__(file_path, channels)
    def save(self):
        """ Save of the data to a root file."""
        self._file = ROOT.TFile(self._file_path, "RECREATE")
        self._tree = ROOT.TTree("T", "Data tree")
        self._branch_hists = {}
        for channel in self._data.keys:
            self._branch_hists[channel] = self._data[channel][0]
            self._tree.Branch("channel_%i" % channel, "TH1D", self._hists[channel])
        # Er??

    def load(self):
        """ Load the data from a root file."""

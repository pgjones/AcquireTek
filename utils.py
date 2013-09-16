#!/usr/bin/env python
#
# utils.py
#
# Utility functions to save waveforms in various formats.
#
# Author P G Jones - 06/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import re
import os
import shutil

class File(object):
    """ Generic file, no saving."""
    def __init__(self, file_path, channels, extension):
        """ Intialise the data structure."""
        self._file_path = file_path
        self._extension = extension
        self._data = {} # Dict by channel or list of waveforms
        for channel in range(1, channels + 1):
            self._data[channel] = []
        self._meta_data = {} # Meta data dict
    def add_meta_dict(self, dict, prefix=""):
        """ Set the meta data for a whole dict."""
        for key in dict.keys():
            self._meta_data[prefix + key] = dict[key]
    def add_meta_data(self, key, data):
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
    def autosave(self):
        """ Save the data into a backup."""
        if os.path.isfile(self._file_path + self._extension):
            shutil.copyfile(self._file_path + self._extension, self._file_path + "_bk" + self._extension)
        self._save(self._file_path + self._extension)
    def save(self):
        self._save(self._file_path + self._extension)
        if os.path.isfile(self._file_path + "_bk" + self._extension):
            os.remove(self._file_path + "_bk" + self._extension)
#--- To Override -----------------------------------------------------------------------------------
    def close(self):
        """ Close/finish."""
        pass
    def _save(self, file_path):
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
        super(PickleFile, self).__init__(file_path, channels, ".pkl")
    def _save(self, file_path):
        """ Save of the data to a pickle file."""
        full_data = { "meta" : self._meta_data,
                      "data" : self._data }
        with open(file_path, "wb") as file_:
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
        super(HDF5File, self).__init__(file_path, channels, ".hdf5")
    def _save(self, file_path):
        """ Save of the data to a hdf5 file."""
        with h5py.File(file_path, "w") as file_:
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
        super(ROOTFile, self).__init__(file_path, channels, ".root")
    def save(self, file_path):
        """ Save of the data to a root file."""
        self._file = ROOT.TFile(file_path, "RECREATE")
        self._tree = ROOT.TTree("T", "Data tree")
        self._branch_hists = {}
        for channel in self._data.keys:
            self._branch_hists[channel] = self._data[channel][0]
            self._tree.Branch("channel_%i" % channel, "TH1D", self._hists[channel])
        # Er??

    def load(self):
        """ Load the data from a root file."""

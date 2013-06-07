#!/usr/bin/env python
#
# root_utils.py
#
# Utility functions to convert waveforms to the high energy physics root format and save the data.
#
# Author P G Jones - 04/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import ROOT

def waveform_to_hist(data_forms, data_units, title="hist"):
    """ Pass a tuple of dataforms and data units."""
    histogram = ROOT.TH1D("data", title, len(data_forms[0]), data_forms[0][0], data_forms[0][-1])
    histogram.SetDirectory(0)
    for index, data in enumerate(data_forms[1]):
        histogram.SetBinContent(index + 1, data)
    histogram.GetXaxis().SetTitle(data_units[0])
    histogram.GetYaxis().SetTitle(data_units[1])
    return histogram

class WaveformFile(object):
    """ A root file filled with waveforms."""
    def __init__(self, file_path, channels):
        """ Initialise by opening the root file and specifying the number of channels to save."""
        self._file = ROOT.TFile(file_path, "RECREATE")
        self._tree = ROOT.TTree("T", "Data tree")
        self._hists = {}
        for channel in range(1, channels + 1):
            self._hists[channel] = ROOT.TH1D()
            self._tree.Branch("channel_%i" % channel, "TH1D", self._hists[channel])
    def close(self):
        """ Close the file."""
        self._tree.Write()
        self._file.Close()
    def set_dataform(self, data_forms, data_units, channel):
        """ Save the data to the ttree."""
        waveform_to_hist(data_forms, data_units)
        self._hists[channel] = waveform_to_hists(data_forms, data_units)
    def save(self):
        """ Save the current hists."""
        self._tree.Fill()

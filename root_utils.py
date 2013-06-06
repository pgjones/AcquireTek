#!/usr/bin/env python
#
# root_utils.py
#
# Utility functions to convert waveforms to the high energy physics root format and save the data.
#
# Author P G Jones - 04/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import ROOT
import array
c1 = ROOT.TCanvas()

def waveform_to_hist(data_forms, data_units, title="hist"):
    """ Pass a tuple of dataforms and data units."""
    histogram = ROOT.TH1D("data", title, len(data_forms[0]), data_forms[0][0], data_forms[0][-1])
    histogram.SetDirectory(0)
    for index, data in enumerate(data_forms[1]):
        histogram.SetBinContent(index + 1, data)
    histogram.GetXaxis().SetTitle(data_units[0])
    histogram.GetYaxis().SetTitle(data_units[1])
    histogram.Draw()
    c1.Update()
    return histogram

def integrate_signal(histogram, trigger=0.0):
    """ Return the integral of the signal pulse, assumed to be at trigger."""
    zero_bin = histogram.GetXaxis().FindBin(0.0) # Find the bin for time 0 (trigger)
    center_bin = zero_bin
    for bin in range(zero_bin, histogram.GetNbinsX()):
        if histogram.GetBinContent(bin) > trigger:
            centre_bin = bin
            break
        if bin == histogram.GetNbinsX() - 1:
            return 0.0 # No Trigger
    sig = [centre_bin, centre_bin + 1] # Signal start/end
    for bin in range(centre_bin, 0, -1): # Find signal start
        if histogram.GetBinContent(bin) <= 0.0:
            sig[0] = bin
            break
    for bin in range(centre_bin, histogram.GetNbinsX()):
        if histogram.GetBinContent(bin) <= 0.0:
            sig[1] = bin
            break
    return histogram.Integral(sig[0], sig[1])

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

class ValueFile(object):
    """ A root file filled with integral values."""
    def __init__(self, file_path, channels):
        """ Initialise by opening the root file and specifying the number of channels to save."""
        self._file = ROOT.TFile(file_path, "RECREATE")
        self._tree = ROOT.TTree("T", "Data tree")
        self._values = {}
        for channel in range(1, channels + 1):
            self._values[channel] = array.array('f', [0])
            self._tree.Branch("channel_%i" % channel, self._values[channel], "value/F")
    def close(self):
        """ Close the file."""
        self._tree.Write()
        self._file.Close()
    def set_data(self, data, channel):
        """ Save the data to the ttree."""
        self._values[channel] = data
    def save(self):
        """ Save the current hists."""
        self._tree.Fill()

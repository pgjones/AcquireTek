#!/usr/bin/env python
#
# root_utils.py
#
# Utility functions to convert waveforms to the high energy physics root format and save the data.
#
# Author P G Jones - 04/06/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import ROOT

def waveform_to_hist(timeform, waveform, data_units, title="hist"):
    """ Pass a tuple of dataforms and data units."""
    histogram = ROOT.TH1D("data", title, len(timeform), timeform[0], timeform[-1])
    histogram.SetDirectory(0)
    for index, data in enumerate(waveform):
        histogram.SetBinContent(index + 1, data)
    histogram.GetXaxis().SetTitle(data_units[0])
    histogram.GetYaxis().SetTitle(data_units[1])
    return histogram

#!/usr/bin/env python
#
# acquire_pmt_data.py
#
# Acquisition of PMT Data from a Tektronix scope
#
# Author P G Jones - 31/05/2013 <p.g.jones@qmul.ac.uk> : First revision
#################################################################################################### 
import scope_connections
import scopes
import numpy
import ROOT
import time

usb_conn = scope_connections.VisaUSB()
tek_scope = scopes.TektronixMSO2000(usb_conn)
tek_scope.lock()
trigger = 0.03 # Volts
tek_scope.set_trigger(-trigger, 1, True) 
integrals_1 = ROOT.TH1D("integrals", "integrals 1", 1000, 0.0, 10.0)
integrals_2 = ROOT.TH1D("integrals", "integrals 2", 1000, 0.0, 10.0)
c1 = ROOT.TCanvas()
c1.Divide(2, 2)
keep = None
t_start = time.time()
acquire_time = 30 * 60 # in seconds
print "Started at", t_start
while time.time() - t_start < acquire_time:
    tek_scope.acquire()
    # Channel 1
    try:
        wave_time, wave_data = tek_scope.get_waveform(1)
        hist_1 = ROOT.TH1D("hist", "hist", len(wave_time), wave_time[0], wave_time[-1])
        for index, a in enumerate(wave_data):
            hist_1.SetBinContent(index + 1, -a) # Invert spectrum
        integrals_1.Fill(hist_1.Integral(hist_1.FindFirstBinAbove(trigger), hist_1.FindLastBinAbove(trigger)))
        # Channel 2
        wave_time, wave_data = tek_scope.get_waveform(2)
        hist_2 = ROOT.TH1D("hist", "hist", len(wave_time), wave_time[0], wave_time[-1])
        for index, a in enumerate(wave_data):
            hist_2.SetBinContent(index + 1, -a) # Invert spectrum
        integrals_1.Fill(hist_2.Integral(hist_2.FindFirstBinAbove(trigger), hist_2.FindLastBinAbove(trigger)))
        
        c1.cd(1)
        hist_1.Draw()
        c1.cd(2)
        hist_2.Draw()
        c1.cd()
        keep = (hist_1, hist_2)
    except Exception:
        print "Scope died."
    c1.Update()

tek_scope.unlock()
c1.cd(3)
integrals_1.Draw()
c1.cd(4)
integrals_2.Draw()
c1.cd()
c1.Update()
raw_input("Wait")

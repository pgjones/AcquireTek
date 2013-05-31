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
tek_scope.set_trigger(-0.1, 1, True) # -200 mV level
integrals = ROOT.TH1D("integrals", "integrals", 100, 0.0, 2.0)
c1 = ROOT.TCanvas()
for acquisition in range(0, 100):
    t0 = time.time()
    tek_scope.acquire()
    wave_time, wave_data = tek_scope.get_waveform(1)
    hist = ROOT.TH1D("hist", "hist", len(wave_time), wave_time[0], wave_time[-1])
    for index, a in enumerate(wave_data):
        hist.SetBinContent(index + 1, -a) # Invert spectrum
    integrals.Fill(hist.Integral(hist.FindFirstBinAbove(0.1), hist.FindLastBinAbove(0.1)))
    hist.Draw() 
    c1.Update()
    print time.time() - t0
tek_scope.unlock()
integrals.Draw()
c1.Update()
raw_input("Wait")

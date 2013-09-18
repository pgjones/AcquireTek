## AcquireTek
Code to acquire data from a tektronix MSO2000 scope. 

### Pre requisits
 - python > 2.5
 - NI VISA (it is free)
 - PyVISA

### Data type
Data is retrieved in units of divs, to convert to volts & time (y & x) the preamble must be used such that:
```python
y_true = (y_data - YZERO) * YMULT
x_true = (x_data - XZERO) * XMULT
```

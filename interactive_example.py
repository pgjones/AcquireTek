#!/usr/bin/env python
#
# interactive_example.py
#
# Simple script to gain interactive control over the scope.
#
# Author P G Jones - 2013-10-23 <p.g.jones@qmul.ac.uk> : First revision
################################################################################## 
import scopes
import scope_connections

tek_scope = scopes.Tektronix2000(scope_connections.VisaUSB())
tek_scope.interactive()

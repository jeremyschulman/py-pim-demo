#!/usr/bin/env python2.7

import argparse
import os,sys
from os.path import splitext, basename

from pprint import pprint as pp
from collections import Counter
from jnpr.junos.factory import loadyaml

def parseargs():
  p = argparse.ArgumentParser(add_help=True)

  # ---------------------------------------------------------------------------
  # PIM arguments
  # ---------------------------------------------------------------------------

  p.add_argument('-U','--upf',
    help="upstream device XML filename")

  p.add_argument('-u','--upi',
    help='upstream device interface name')

  p.add_argument('-D', '--dnf',
    help='downstream device XML filename')

  p.add_argument('-d','--dni',
    help='downstream device interface name')

  return p.parse_args()  

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

args = parseargs()  

def die(msg):
  sys.stderr.write("ERROR: {}\n".format(msg))
  sys.exit(1)

if args.upf is None: die("You must specify -U")
if args.dnf is None: die("You must specify -D")
if args.upi is None: die("You must specify -i")
if args.dni is None: die("You must specify -d")

PimJoinTable = loadyaml("defs-pim.yml")['PimJoinTable']

up = PimJoinTable(path=args.upf).get()
dn = PimJoinTable(path=args.dnf).get()

if not '.' in args.dni: args.dni += '.0'
if not '.' in args.upi: args.upi += '.0'

# upstream is easy since there is only 1 up_iface per (S,G)
up_keys = set([i.name for i in up if i.up_iface == args.upi])

# downstream is tricky since there can be many per (S,G)
dn_keys = set([i.name for i in dn if args.dni in i.dn_iface])

missing = up_keys - dn_keys
print "MISSING {} (S,G) entries".format(len(missing))
for each in missing:
  print each











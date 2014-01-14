#!/usr/bin/env python2.7

import argparse
import os,sys
from os.path import splitext, basename
from itertools import chain
from pprint import pprint as pp
from collections import Counter
from jnpr.junos.factory import loadyaml

def parseargs():
  p = argparse.ArgumentParser(add_help=True)

  # ---------------------------------------------------------------------------
  # PIM arguments
  # ---------------------------------------------------------------------------

  p.add_argument('file',
    help="filename of XML data")

  p.add_argument('-i','--iface', action='append',
    help='interface name(s)')

  p.add_argument('-d','--dir', nargs='?', choices=['up','dn'], default='up',
    help='interface direction')

  p.add_argument('-l','--list', action='store_true',
    help='list interfaces and counts for given <dir>')

  return p.parse_args()  

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

args = parseargs()  


PimJoinTable = loadyaml("defs-pim.yml")['PimJoinTable']
pimjoin = PimJoinTable(path=args.file).get()

# auto-append '.0' if IFL not specified
if args.iface is not None:
  for i,v in enumerate(args.iface):
    if not '.' in v: args.iface[i]  += '.0'

def show_iface_counts(iface_cntr):
  iface_list = iface_cntr.keys() if args.iface is None else args.iface
  total_count = 0
  for iface in iface_list:
    if not iface_cntr.has_key(iface): continue    
    this_count = iface_cntr[iface]
    total_count += this_count
    print "  {}: {} entries".format(iface, this_count)
  print "TOTAL: {}".format(total_count)

def list_up_ifaces():
  iface_cntr = Counter([x.up_iface for x in pimjoin])
  print "UPSTREAM COUNTERS:"  
  show_iface_counts(iface_cntr)

def list_dn_ifaces():
  # each (S,G) could actually have multiple downstream
  # interfaces, so we need to account for this, yo!
  _dn_1 = [i.dn_iface for i in pimjoin if i.dn_iface_count == 1]
  _dn_n = [i.dn_iface for i in pimjoin if i.dn_iface_count > 1]
  iface_cntr = Counter(_dn_1)
  iface_cntr.update(Counter(chain.from_iterable(_dn_n)))
  print "DOWNSTREAM COUNTERS:"
  show_iface_counts(iface_cntr)

#### --------------------------------------------------------------------------
#### --list interface(s) counts
#### --------------------------------------------------------------------------

if args.list is True:
  {
    'up': list_up_ifaces,
    'dn': list_dn_ifaces
  }[args.dir]()
  sys.exit(0)

#### --------------------------------------------------------------------------
#### showing (S,G) for interface(s)
#### --------------------------------------------------------------------------

if args.iface is None:
  sys.stderr.write("ERROR: you must provide at least one <iface>\n")
  sys.exit(1)

if args.dir == 'up':
  matching = [i for i in pimjoin if i.up_iface in args.iface]
  matching.sort(key=lambda x: x.up_iface)
  for each in matching:
    print "{}:{}".format(each.up_iface, each.name)
else:
  # each (S,G) could actually have multiple downstream
  # interfaces, so we need to account for this, yo!
  _dn_1 = [i for i in pimjoin if i.dn_iface_count == 1]
  _dn_n = [i for i in pimjoin if i.dn_iface_count > 1]

  matching = [i for i in _dn_n if \
    any([True for each in i.dn_iface if each in args.iface])]
  matching.extend([i for i in _dn_1 if i.dn_iface in args.iface])

  for each in matching:
    print "{}".format(each.name)
#!/usr/bin/env python2.7

import argparse
import os,sys

from getpass import getpass
from pprint import pprint as pp
from collections import Counter
from itertools import chain

from jnpr.junos import Device
from jnpr.junos.factory import loadyaml
from jnpr.junos.exception import RpcError

def parseargs():
  p = argparse.ArgumentParser(add_help=True)

  # ---------------------------------------------------------------------------
  # login arguments
  # ---------------------------------------------------------------------------

  p.add_argument('name', 
    help='Name of Junos device')
  p.add_argument('-u','--user', 
    help='Login user name')
  p.add_argument('-k', action='store_true', dest='passwd_prompt', 
    default=False,
    help='Prompt login password, assumes ssh-keys otherwise')

  # ---------------------------------------------------------------------------
  # PIM arguments
  # ---------------------------------------------------------------------------

  p.add_argument('-L','--lsys',
    help="Pull PIM from logical-system")

  p.add_argument('-s','--save', default='yes',
    help="save XML filename, or defaults to hostname")

  return p.parse_args()  

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

args = parseargs()  
login_user = args.user or os.getenv('USER')
login_passwd = '' if args.passwd_prompt is False else getpass()

# -------------------------
# open connection to device
# -------------------------

print "connecting to {} ...".format(args.name)
dev = Device(args.name,user=login_user,password=login_passwd)
try:
  dev.open()
except Exception as err:
  sys.stderr.write("ERROR: Login failure.  Try again, use '-k' for password prompt\n")
  sys.exit(1)

# ------------------------------
# get PIM JOIN table information
# ------------------------------

print "retrieving PIM join table ..."
PimJoinTable = loadyaml("defs-pim.yml")['PimJoinTable']
pimjoin = PimJoinTable(dev)

kvargs = {'extensive':True}
if args.lsys is not None: 
  kvargs['logical-system'] = args.lsys

try:
  pimjoin.get(**kvargs)
except RpcError as err:
  err_msg = err.rsp.findtext('.//error-message').strip()
  sys.stderr.write("ERROR: {}\n".format(err_msg))
  dev.close()
  sys.exit(1)

dev.close()

# ---------------------------------
# save
# ---------------------------------

save_name = args.name+'.xml' if args.save == 'yes' else args.save
print "saving to: {}".format(save_name)
pimjoin.savexml(save_name)


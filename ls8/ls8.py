#!/usr/bin/env python3

"""Main."""

import sys
import os
from cpu import *

cpu = CPU()

# Make sure second argument is passed
if len(sys.argv) <= 1:
  raise Exception('Program is expected as a second argument, None provided.')
else:
  # Validate that the argument given is a file that exists
  file = sys.argv[1]

  if os.path.isfile(file):
    # Load filename into CPU
    cpu.load(file)
    cpu.run()
  else:
    raise FileNotFoundError('Could not find the specified file.')
  
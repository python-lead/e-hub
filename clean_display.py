#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'e-hub/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.DEBUG)

try:
    epd = epd7in5_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()

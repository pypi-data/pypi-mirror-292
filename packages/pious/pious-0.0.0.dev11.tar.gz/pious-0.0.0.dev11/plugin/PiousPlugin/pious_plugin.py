from pious.pio.plugin import PioPlugin

from os import path as osp
import datetime as dt
import os

with open(osp.join(osp.expanduser("~"), "pious-test.txt"), "w") as f:
    f.write(str(dt.datetime.now()))
    f.write("\n")
    f.flush()
plugin = PioPlugin()
plugin.run_plugin()

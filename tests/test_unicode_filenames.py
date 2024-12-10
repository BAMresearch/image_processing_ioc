# import epics # attention, pyepics cuts the path after 4 characters!
import caproto.threading.pyepics_compat as epics
from pathlib import Path

testpath = Path('./tests')
for fname in testpath.glob('*h5'):
    print(f"working on file {fname}")
    epics.caput('image:ImagePathPrimary', str(fname).encode('utf-8'))
    epics.caput('image:ImagePathSecondary', str(fname).encode('utf-8'))

    print(epics.caget("image:primary:total_counts"))
    print(epics.caget("image:secondary:total_counts"))
    print(epics.caget("image:ratio"))

"""Python 2 vs 3 compatibility."""
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    string_types = (str, unicode)
    print_bytes = lambda s: sys.stdout.write(s)
else:
    string_types = (str,)
    print_bytes = lambda s: sys.stdout.buffer.write(s)

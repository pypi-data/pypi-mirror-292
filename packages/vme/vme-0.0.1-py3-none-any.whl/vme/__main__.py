if __name__ != '__main__':
    exit(0)

from . import send
import sys

send(sys.argv[1], ' '.join(sys.argv[2:]))

### vme/__main__.py ends here

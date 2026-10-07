"""Import this first in every test file that runs the engine. GlooClient() loads the repo-root .env when it is built,
which would turn on the live YouVersion provider inside tests. Tests must never reach the network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import os  # noqa: E402

from nury import gloo_client  # noqa: E402,F401



def scrub():
    """Another test may build a GlooClient, which loads .env again. Call this in setUp of any test that picks a verse."""
    for k in ("YVP_APP_KEY", "YVP_BIBLE_ES", "YVP_BIBLE_EN", "JEV_API_KEY"):
        os.environ.pop(k, None)
    os.environ["NURY_JEV_GATE"] = "off"      # a test that wants the gate turns it on and patches requests.post


def _guard_network():
    """A test may talk to this machine (the servers the tests start) and nothing else: any other address raises."""
    import socket
    real = socket.socket.connect
    if getattr(real, "_nury_guard", False):
        return

    def guarded(self, address):
        host = address[0] if isinstance(address, tuple) else address
        if isinstance(address, tuple) and str(host) not in ("127.0.0.1", "::1", "localhost"):
            raise OSError(f"tests must not reach the network: {host}")
        return real(self, address)
    guarded._nury_guard = True
    socket.socket.connect = guarded


_guard_network()
scrub()

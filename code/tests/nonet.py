"""Import this first in every test file that runs the engine. The Gloo client loads the repo-root .env on import,
which would turn on the live YouVersion provider inside tests. Tests must never reach the network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import os  # noqa: E402

from nury import gloo_client  # noqa: E402,F401



def scrub():
    """Another test may build a GlooClient, which loads .env again. Call this in setUp of any test that picks a verse."""
    for k in ("YVP_APP_KEY", "YVP_BIBLE_ES", "YVP_BIBLE_EN"):
        os.environ.pop(k, None)


scrub()

"""Compatibility entry point for the current anchored-deck UI regression suite."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('test-ui-deck.py')),run_name='__main__')

"""Add only the explicit bundled application directory to an isolated Python."""
import runpy,sys
from pathlib import Path

entry=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(entry.parent))
sys.argv=sys.argv[1:]
runpy.run_path(str(entry),run_name='__main__')

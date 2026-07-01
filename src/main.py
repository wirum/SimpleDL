import sys
from pathlib import Path
import importlib

# adiciona o diretório src ao sys.path quando executado de dentro de src/
src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    run_cli = importlib.import_module('cli').run_cli
except ImportError:
    run_cli = importlib.import_module('simpledl.cli').run_cli


if __name__ == '__main__':
    run_cli()

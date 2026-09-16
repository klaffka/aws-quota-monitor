"""Compatibility CLI for the maintained CSV reporting entry point."""
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
lambda_handler = importlib.import_module('functions.reporting.main').lambda_handler

if __name__ == '__main__':
    event = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(json.dumps(lambda_handler(event, None), indent=2))

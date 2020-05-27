import argparse
from pathlib import Path

from . import manager, server

def main():
    parser = argparse.ArgumentParser(description='Archive Box')
    parser.add_argument('--workspace', type=str, nargs=1, required=True)

    args = parser.parse_args()
    workspace = Path(args.workspace)
    manager.load_workspace(workspace)

    while True:
        manager.maybe_sync()
        server.run(manager.get().config)

if __name__ == "__main__":
    main()

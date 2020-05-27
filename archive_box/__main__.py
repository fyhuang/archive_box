import argparse
from pathlib import Path

from . import manager, server

def main() -> None:
    parser = argparse.ArgumentParser(description='Archive Box')
    parser.add_argument('--workspace', type=str, nargs=1, required=True)

    args = parser.parse_args()
    workspace = Path(args.workspace[0])
    manager.load_workspace(workspace)

    while True:
        server.run(manager.get().config)
        synced = manager.get().maybe_sync()
        if not synced:
            break

if __name__ == "__main__":
    main()

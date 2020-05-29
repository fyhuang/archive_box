import argparse
from pathlib import Path

#from . import manager, server, ingestor

def main() -> None:
    parser = argparse.ArgumentParser(description='Archive Box')
    parser.add_argument('--workspace', type=str, nargs=1, required=True)

    args = parser.parse_args()
    workspace = Path(args.workspace[0])
    #manager.load_workspace(workspace)

    #while True:
    #    ingestor.start_ingestor_thread()
    #    server.run(manager.get().config)
    #    ingestor.stop_ingestor_thread()

    #    synced = manager.get().maybe_sync()
    #    if not synced:
    #        break

if __name__ == "__main__":
    main()

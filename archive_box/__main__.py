import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Archive Box')
    parser.add_argument('--workspace', type=str, nargs=1, required=True)

    args = parser.parse_args()
    workspace = Path(args.workspace)
    while True:
        server = Server(workspace)
        server.maybe_sync()
        server.run()

if __name__ == "__main__":
    main()

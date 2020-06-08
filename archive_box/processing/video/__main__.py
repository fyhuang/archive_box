import argparse
from pathlib import Path

from . import transcode
from .config import *

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("config")
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    config = TranscodeConfig([
        #TargetRepresentation.for_quality("360p", "av1"),
        TargetRepresentation.for_quality("720p", "av1"),
    ])

    transcode.do_transcode(Path(args.input), config)

if __name__ == "__main__":
    main()

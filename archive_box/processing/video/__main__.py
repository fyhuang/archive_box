import argparse
from pathlib import Path

import toml

import cfgparse

from . import transcode, ffprobe
from .config import *

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("input")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        raw_config = toml.load(f)
    config = cfgparse.mapping_to_nt(raw_config, TranscodeConfig)

    # print input representation
    input_repr = ffprobe.guess_file_repr(Path(args.input))
    print("Input file has representation: {}".format(input_repr))

    transcode.transcode_all(Path(args.input), Path(args.output_dir), config)

if __name__ == "__main__":
    main()

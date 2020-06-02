import argparse
import json
import sys
from typing import Any

from . import text
from .text.summary import *

def output_text_to_file(value: Any, filename: str):
    if isinstance(value, str):
        value_str = value
    else:
        value_str = json.dumps(value)

    if len(filename) == 0:
        raise RuntimeError("must specify output file (or - for stdout)")
    elif filename == "-":
        # output to stdout
        sys.stdout.write(value_str)
        sys.stdout.write("\n")
    else:
        with open(filename, "w") as f:
            f.write(value_str)

def try_process_text(args) -> None:
    extracted_text = text.extract.extract_text(args.input)
    if args.text_out:
        output_text_to_file(extracted_text, args.text_out)

    summary = text_to_summary(extracted_text)
    if args.summary_out:
        output_text_to_file(summary, args.summary_out)

    keywords = text_to_keywords(extracted_text)
    if args.keywords_out:
        output_text_to_file(keywords, args.keywords_out)

def main() -> None:
    parser = argparse.ArgumentParser(description="Apply processing on input files")
    parser.add_argument('input', type=str)
    parser.add_argument('--text_out', type=str)
    parser.add_argument('--summary_out', type=str)
    parser.add_argument('--keywords_out', type=str)
    args = parser.parse_args()

    try_process_text(args)

if __name__ == "__main__":
    main()

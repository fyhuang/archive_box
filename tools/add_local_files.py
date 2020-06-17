import argparse
from pathlib import Path
from typing import Dict

import requests


def add_one(args, full_path: Path, root_dir: Path) -> Dict:
    relative_path = full_path.relative_to(root_dir)

    tags = []
    if args.dirs_as_tags:
        tags = list(relative_path.parent.parts)

    doc_params = {
        "source": str(full_path),
        "tags": tags,
        "base_path": str(root_dir),
    }
    print(doc_params)

    api_url = "{}/api/create_document/{}".format(args.abox, args.cid)
    response = requests.post(api_url, json=doc_params)
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('cid')
    parser.add_argument('input_dir')
    parser.add_argument('--abox', default='http://localhost:8123')
    # organizational options
    parser.add_argument('--dirs_as_tags', action='store_true')

    args = parser.parse_args()

    root_dir = Path(args.input_dir).resolve()
    for file in root_dir.glob("**/*"):
        if not file.is_file():
            continue
        status = add_one(args, file, root_dir)
        if "doc_id" in status:
            print("{} -> {}".format(file, status["doc_id"]))
        else:
            print("{} -> (duplicate)".format(file))


if __name__ == "__main__":
    main()

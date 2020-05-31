import os
import secrets
from pathlib import Path
from typing import Any, Set, Mapping, NamedTuple

import toml

from dtsdb.node_config import NodeConfig


def _default_node_name():
    hostname = socket.gethostname()
    if len(hostname) == 0:
        return "unknown node"
    else:
        return hostname


class Workspace(NamedTuple):
    root_path: Path
    internal_path: Path
    config: Mapping[str, Any]
    node_config: NodeConfig

    @staticmethod
    def load_from_path(root_path: Path) -> 'Workspace':
        if not root_path.exists():
            raise RuntimeError("Workspace {} must exist already".format(root_path))

        internal = root_path / "internal"
        os.makedirs(internal, exist_ok=True)

        node_config_path = internal / "node_config.toml"
        if node_config_path.exists():
            with node_config_path.open("r") as f:
                node_config = NodeConfig.from_toml(f.read())
        else:
            node_config = NodeConfig(secrets.randbelow(2**63), _default_node_name())
            with node_config_path.open("w") as f:
                f.write(node_config.to_toml())

        with open(root_path / "config.toml", "r") as f:
            config = toml.load(f)

        return Workspace(root_path, internal, config, node_config)

    def inbox_path(self) -> Path:
        return Path(self.config["server"]["inbox"])

    def scanner_db_path(self) -> Path:
        return self.internal_path / "scanner.db"

    def collection_db_path(self, cid: str) -> Path:
        return self.internal_path / "c_{}.db".format(cid)

    def cids(self) -> Set[str]:
        return set(self.config.get("collections", {}).keys())

    def collection_config(self, cid: str) -> Mapping[str, Any]:
        return self.config["collections"][cid]
from pathlib import Path
from typing import Any

class Globals(object):
    def __init__(self):
        self.workspace = None
        self.internal = None
        self.node_config = None
        self.config = None
        self.lock = threading.Lock()

    def load_workspace(self, workspace: Path) -> None:
        with self.lock:
            self.workspace = workspace
            self.internal = workspace / "internal"
            os.makedirs(self.internal, exist_ok=True)

            node_config_path = self.internal / "node_config.toml"
            if node_config_path.exists():
                with node_config_path.open("r") as f:
                    self.node_config = NodeConfig.from_toml(f.read())
            else:
                self.node_config = NodeConfig(secrets.randbelow(2**63), os.env["HOSTNAME"])
                with node_config_path.open("w") as f:
                    f.write(self.node_config.to_toml())

            with open(workspace / "config.toml", "r") as f:
                self.config = toml.load(f)

app = Flask(__name__)
globals = Globals()


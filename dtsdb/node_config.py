import collections

import toml

class NodeConfig(
    collections.namedtuple("NodeConfig", ["clock_id", "display_name"])
):
    # TODO(fyhuang): just make it read from a file object
    @staticmethod
    def from_toml(in_toml: str) -> 'NodeConfig':
        parsed = toml.loads(in_toml)
        return NodeConfig(int(parsed["node"]["clock_id"]), parsed["node"]["display_name"])

    def to_toml(self) -> str:
        toml_dict = {"node": {
            "clock_id": self.clock_id,
            "display_name": self.display_name,
        }}
        return toml.dumps(toml_dict)

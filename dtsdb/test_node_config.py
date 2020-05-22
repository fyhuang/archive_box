import unittest

from .node_config import *

class NodeConfigTests(unittest.TestCase):
    def test_from_toml(self) -> None:
        t = """
        [node]
        clock_id = "123"
        display_name = "my node"
        """
        nc = NodeConfig.from_toml(t)
        self.assertEqual(
            NodeConfig(123, "my node"),
            nc
        )

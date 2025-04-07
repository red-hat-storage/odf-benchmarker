import unittest
from metrics_generator import generate_node_specific_metrics


class TestGenerateNodeSpecificMetrics(unittest.TestCase):
    def setUp(self):
        self.metrics_dict = {
            "storage": {
                "blocksizes": ["4k", "16k"],
                "workloads": ["read", "write"],
                "threads": [1, 2],
                "flags": ["sync", "direct"]
            },
            "network": {
                "threads": [1, 2],
                "workloads": ["ping", "iperf"]
            },
            "cpu": {
                "parameters": ["param1", "param2"]
            }
        }

        self.resources_dict = {
            "nodes": [
                {
                    "node_name": "node1",
                    "disks": ["sda", "sdb"],
                    "network_interfaces": ["eth0", "eth1"]
                },
                {
                    "node_name": "node2",
                    "disks": ["sdc", "sdd"],
                    "network_interfaces": ["eth2", "eth3"]
                }
            ]
        }

    def test_generate_metrics_for_existing_node(self):
        node_name = "node1"
        result = generate_node_specific_metrics(
            self.metrics_dict, self.resources_dict, node_name)

        expected = {
            "storage": {
                "disks": [{"path": "/dev/sda"}, {"path": "/dev/sdb"}],
                "blocksizes": ["4k", "16k"],
                "workloads": ["read", "write"],
                "threads": [1, 2],
                "flags": ["sync", "direct"]
            },
            "network": {
                "interfaces": ["eth0", "eth1"],
                "threads": [1, 2],
                "peers": ["node2"],
                "workloads": ["ping", "iperf"]
            },
            "cpu": {
                "parameters": ["param1", "param2"]
            }
        }

        self.assertEqual(result, expected)

    def test_generate_metrics_for_nonexistent_node(self):
        node_name = "node3"
        with self.assertRaises(ValueError) as context:
            generate_node_specific_metrics(
                self.metrics_dict, self.resources_dict, node_name)

        self.assertEqual(str(context.exception),
                         "Node 'node3' not found in resources.json")

    def test_generate_metrics_with_empty_resources(self):
        empty_resources_dict = {"nodes": []}
        node_name = "node1"
        with self.assertRaises(ValueError) as context:
            generate_node_specific_metrics(
                self.metrics_dict, empty_resources_dict, node_name)

        self.assertEqual(str(context.exception),
                         "Node 'node1' not found in resources.json")

    def test_generate_metrics_with_missing_fields(self):
        incomplete_resources_dict = {
            "nodes": [
                {
                    "node_name": "node1",
                    # Missing 'disks' and 'network_interfaces'
                }
            ]
        }
        node_name = "node1"
        with self.assertRaises(KeyError):
            generate_node_specific_metrics(
                self.metrics_dict, incomplete_resources_dict, node_name)


if __name__ == "__main__":
    unittest.main()

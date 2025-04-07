import json


def generate_node_specific_metrics(metrics_dict, resources_dict, node_name):
    # Find node in resources.json
    node = next(
        (n for n in resources_dict["nodes"] if n["node_name"] == node_name), None)
    if not node:
        raise ValueError(f"Node '{node_name}' not found in resources.json")

    # Extract peers (all other nodes)
    peers = [
        n["node_name"] for n in resources_dict["nodes"]
        if n["node_name"] != node_name
    ]

    # Build the per-node benchmark dictionary
    node_metrics = {
        "storage": {
            "disks": [{"path": f"/dev/{d}"} for d in node["disks"]],
            "blocksizes": metrics_dict["storage"]["blocksizes"],
            "workloads": metrics_dict["storage"]["workloads"],
            "threads": metrics_dict["storage"]["threads"],
            "flags": metrics_dict["storage"]["flags"]
        },
        "network": {
            "interfaces": node["network_interfaces"],
            "threads": metrics_dict["network"]["threads"],
            "peers": peers,
            "workloads": metrics_dict["network"]["workloads"]
        },
        "cpu": {
            "parameters": metrics_dict["cpu"]["parameters"]
        }
    }

    return node_metrics

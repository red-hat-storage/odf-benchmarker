import os
import sys
import pytest
from unittest import mock

# Patch sys.argv and os.environ for the test
@mock.patch.dict(os.environ, {"NODE_NAME": "myathnal-bench-fs6km-worker-1-sgh56"})
@mock.patch("builtins.open", new_callable=mock.mock_open, read_data='{}')
@mock.patch("json.load", side_effect=[
    {
        "nodes": [
            {
                "node_name": "myathnal-bench-fs6km-worker-1-sgh56",
                "disks": ["nbd0"],
                "network_interfaces": ["ens3"]
            }
        ]
    },
    {
        "storage": {"blocksizes": ["4k"], "workloads": ["seqwr"], "threads": [1], "flags": [{"file-extra-flags": "dsync"}]},
        "network": {"interfaces": ["ens3"], "threads": [1], "peers": [], "workloads": ["iperf"]},
        "cpu": {"parameters": [{"threads": [1], "cpu-max-prime": 1000}]}
    }
])
@mock.patch("src.benchmarker.CPUBenchmarker")
@mock.patch("src.benchmarker.StorageBenchmarker")
@mock.patch("src.benchmarker.NetworkBenchmarker")
def test_main(mock_network, mock_storage, mock_cpu, mock_json_load, mock_open):
    sys.argv = ["benchmarker.py", "--resources", "resources.json", "--metrics", "metrics.json"]
    from src.benchmarker import main
    # Mock run() to return a DataFrame
    import pandas as pd
    mock_cpu.return_value.run.return_value = pd.DataFrame({"a": [1]})
    mock_storage.return_value.run.return_value = pd.DataFrame({"b": [2]})
    mock_network.return_value.run.return_value = pd.DataFrame({"c": [3]})
    main() 
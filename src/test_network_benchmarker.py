""" Pytest for NetworkBenchmark using Mock """

import pytest
import pandas as pd
from unittest import mock
from .network_benchmarker import NetworkBenchmarker
# Pytest for NetworkBenchmark using Mock


def test_network_benchmark():
    mock_config = {
        "interfaces": ["eth0"],
        "peers": ["rhocs-bm7"],
        "threads": [1],
        "workloads": ["iperf", "ping", "hping"]
    }
    benchmark = NetworkBenchmarker(mock_config)

    with mock.patch('subprocess.run') as mocked_run:
        # Setting up the mock to return a successful result for iperf
        mocked_run.return_value.returncode = 0
        mocked_run.return_value.stdout = "iperf3 test successful"
        mocked_run.return_value.stderr = ""

        # Test iperf benchmark
        benchmark.run_iperf_benchmark("eth0", "rhocs-bm7", 1)
        mocked_run.assert_called_with([
            'iperf3', '-c', 'rhocs-bm7', '-B', 'eth0', '-P', '1', '-t', '10'
        ], capture_output=True, text=True)
        assert mocked_run.call_count == 1

        # Setting up the mock to return a successful result for ping
        mocked_run.reset_mock()
        mocked_run.return_value.returncode = 0
        mocked_run.return_value.stdout = "ping test successful\ntime=0.5 ms\ntime=1.0 ms\ntime=2.0 ms\ntime=1.5 ms"
        mocked_run.return_value.stderr = ""

        # Test ping benchmark
        benchmark.run_ping_benchmark("rhocs-bm7")
        mocked_run.assert_called_with([
            'ping', '-c', '10', 'rhocs-bm7'
        ], capture_output=True, text=True)
        assert mocked_run.call_count == 1

        # Setting up the mock to return a successful result for hping
        mocked_run.reset_mock()
        mocked_run.return_value.returncode = 0
        mocked_run.return_value.stdout = "hping3 test successful\nrtt=0.8 ms\nrtt=1.2 ms\nrtt=1.0 ms\nrtt=1.5 ms"
        mocked_run.return_value.stderr = ""

        # Test hping benchmark
        benchmark.run_hping_benchmark("rhocs-bm7")
        mocked_run.assert_called_with([
            'hping3', '-S', 'rhocs-bm7', '-p', '80', '-c', '10'
        ], capture_output=True, text=True)
        assert mocked_run.call_count == 1

        print("Test passed: iperf3, ping, and hping called successfully with expected arguments.")


if __name__ == "__main__":
    pytest.main([__file__])

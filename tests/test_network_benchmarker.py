""" Pytest for NetworkBenchmark using Mock """

import pytest
import pandas as pd
from unittest import mock
from src.network_benchmarker import NetworkBenchmarker
# Pytest for NetworkBenchmark using Mock


def test_network_benchmark():
    mock_config = {
        "interfaces": ["eth0"],
        "peers": ["rhocs-bm7"],
        "threads": [1],
        "workloads": ["iperf", "ping", "hping3"]
    }
    benchmark = NetworkBenchmarker(mock_config)

    with mock.patch('subprocess.run') as mocked_run:
        # iperf3 success
        mocked_run.return_value.returncode = 0
        mocked_run.return_value.stdout = "[SUM] 100 Mbits"
        mocked_run.return_value.stderr = ""
        benchmark.run_iperf_benchmark("eth0", "rhocs-bm7", 1)
        # ping success
        mocked_run.return_value.stdout = "64 bytes from 1.1.1.1: icmp_seq=1 ttl=64 time=0.123 ms"
        benchmark.run_ping_benchmark("rhocs-bm7")
        # hping3 success
        mocked_run.return_value.stdout = "rtt=0.456 ms"
        benchmark.run_hping_benchmark("rhocs-bm7")
        # run() method
        with mock.patch.object(benchmark, 'run_iperf_benchmark') as m1, \
             mock.patch.object(benchmark, 'run_ping_benchmark') as m2, \
             mock.patch.object(benchmark, 'run_hping_benchmark') as m3, \
             mock.patch('time.sleep'):
            m1.return_value = None
            m2.return_value = None
            m3.return_value = None
            df = benchmark.run()
            assert isinstance(df, pd.DataFrame)


def test_network_benchmark_error_branches():
    mock_config = {
        "interfaces": ["eth0"],
        "peers": ["rhocs-bm7"],
        "threads": [1],
        "workloads": ["iperf", "ping", "hping3"]
    }
    benchmark = NetworkBenchmarker(mock_config)

    # iperf3 failure
    with mock.patch('subprocess.run') as mocked_run:
        mocked_run.return_value.returncode = 1
        mocked_run.return_value.stdout = ""
        mocked_run.return_value.stderr = "iperf3 error"
        benchmark.run_iperf_benchmark("eth0", "rhocs-bm7", 1)
    # ping failure
    with mock.patch('subprocess.run') as mocked_run:
        mocked_run.return_value.returncode = 1
        mocked_run.return_value.stdout = ""
        mocked_run.return_value.stderr = "ping error"
        benchmark.run_ping_benchmark("rhocs-bm7")
    # hping3 failure
    with mock.patch('subprocess.run') as mocked_run:
        mocked_run.return_value.returncode = 1
        mocked_run.return_value.stdout = ""
        mocked_run.return_value.stderr = "hping3 error"
        benchmark.run_hping_benchmark("rhocs-bm7")
    # Exception branches
    with mock.patch('subprocess.run', side_effect=Exception("fail")):
        benchmark.run_iperf_benchmark("eth0", "rhocs-bm7", 1)
        benchmark.run_ping_benchmark("rhocs-bm7")
        benchmark.run_hping_benchmark("rhocs-bm7")


if __name__ == "__main__":
    pytest.main([__file__])

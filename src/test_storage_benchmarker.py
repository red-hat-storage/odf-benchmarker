

""" 
This module contains unit tests for the `StorageBenchmarker` class using pytest and unittest.mock.

Fixtures:
    - sysbench_runner_instance: Provides an instance of the `StorageBenchmarker` class initialized with test data.

Mocks:
    - subprocess.run: Mocked to simulate the execution of sysbench commands without actually running them.

Test Data:
    - data: Dictionary containing test parameters for disks, blocksizes, workloads, threads, and flags.

Test Functions:
    - test_sysbench_prepare: Tests the `sysbench_prepare` method.
    - test_sysbench_run: Tests the `sysbench_run` method.
    - test_sysbench_cleanup: Tests the `sysbench_cleanup` method.
    - test_run_all_tests: Tests the `run_all_tests` method.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from .storage_benchmarker import StorageBenchmarker

# Tests using pytest
data: Dict[str, Any] = {
    "disks": ["/dev/nvme2n1"],
    "blocksizes": ["4k", "16k", "128k", "1M", "10M", "100M"],
    "workloads": ["seqwr", "seqrd", "seqrewr", "rndwr", "rndrd", "rndrw"],
    "threads": [4, 8, 16, 32, 64],
    "flags": [
        {
            "file-extra-flags": "dsync"
        }
    ]

}

stdout = """
        File operations:
            reads/s:                      0.00
            writes/s:                     29718.09
            fsyncs/s:                     1191.86

        Throughput:
            read, MiB/s:                  0.00
            written, MiB/s:               116.09

        General statistics:
            total time:                          10.0009s
            total number of events:              309103

        Latency (ms):
             min:                                    0.00
             avg:                                    0.26
             max:                                    8.15
             95th percentile:                        0.00
             sum:                                79932.20
        """


@pytest.fixture
def sysbench_runner_instance():
    """Provides an instance of the `StorageBenchmarker` class initialized"""
    return StorageBenchmarker(data)


@patch('subprocess.run')
def test_sysbench_prepare(mock_run: MagicMock, sysbench_runner_instance: StorageBenchmarker):
    """
    Test the `sysbench_prepare` method of the `StorageBenchmarker` class.
    This test verifies that the `sysbench_prepare` method constructs and 
    executes the correct sysbench command with the given parameters.
    Args:
        mock_run (MagicMock): Mock object for the `subprocess.run` method.
        sysbench_runner_instance (StorageBenchmarker): Instance of the `StorageBenchmarker` class.
    Asserts:
        The `subprocess.run` method is called once with the expected command 
        arguments to prepare the sysbench file I/O test.
    """

    mock_run.return_value = MagicMock()
    sysbench_runner_instance.sysbench_prepare(
        "/dev/nvme2n1", "4k", "seqwr", 4, "dsync")
    mock_run.assert_called_once_with([
        'sysbench',
        '--file-total-size=4k',
        '--file-test-mode=seqwr',
        '--threads=4',
        '--file-extra-flags=dsync',
        'fileio',
        'prepare'
    ], capture_output=True, text=True, check=True)


@patch('subprocess.run')
def test_sysbench_run(mock_run: MagicMock, sysbench_runner_instance: StorageBenchmarker):
    """ test the `sysbench_run` method of the `StorageBenchmarker` class."""
    mock_run.return_value = MagicMock(stdout=stdout)
    sysbench_runner_instance.sysbench_run(
        "/dev/nvme2n1", "4k", "seqwr", 4, "dsync")
    mock_run.assert_called_once_with([
        'sysbench',
        '--file-total-size=4k',
        '--file-test-mode=seqwr',
        '--threads=4',
        '--file-extra-flags=dsync',
        'fileio',
        'run'
    ], capture_output=True, text=True, check=True)
    print(sysbench_runner_instance.results)
    assert sysbench_runner_instance.results[0]['writes/s'] == 29718.09
    assert sysbench_runner_instance.results[0]['latency_max'] == 8.15


@patch('subprocess.run')
def test_sysbench_cleanup(mock_run: MagicMock, sysbench_runner_instance: StorageBenchmarker):
    """ Test the `sysbench_cleanup` method of the `StorageBenchmarker` class."""
    mock_run.return_value = MagicMock()
    sysbench_runner_instance.sysbench_cleanup(
        "/dev/nvme2n1", "4k", "seqwr", 4, "dsync")
    mock_run.assert_called_once_with([
        'sysbench',
        '--file-total-size=4k',
        '--file-test-mode=seqwr',
        '--threads=4',
        '--file-extra-flags=dsync',
        'fileio',
        'cleanup'
    ], capture_output=True, text=True, check=True)


@patch('subprocess.run')
def test_run_all_tests(mock_run: MagicMock, sysbench_runner_instance: StorageBenchmarker):
    mock_run.return_value = MagicMock(stdout=stdout)
    sysbench_runner_instance.run_all_tests()
    assert mock_run.call_count == len(data['blocksizes']) * len(data['workloads']) * len(
        data['threads']) * len(data['flags']) * len(data['disks']) * 3

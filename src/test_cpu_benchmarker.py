from unittest.mock import patch
from unittest.mock import MagicMock
import pytest
import subprocess
from .cpu_benchmarker import CPUBenchmarker

stdout: str = """
        CPU speed:
            events per second: 853267.75

        General statistics:
            total time:                          10.0002s
            total number of events:              8537887

        Latency (ms):
             min:                                    0.00
             avg:                                    0.00
             max:                                    0.07
             95th percentile:                        0.00
             sum:                                 9291.90
        """


@patch('subprocess.run')
def test_sysbench_cpu_runner(mock_subprocess_run: MagicMock):
    """
    Tests the CPUBenchmarker class by mocking subprocess.run to avoid actual sysbench execution.
    """
    # Mocking the return value of subprocess.run
    mock_subprocess_run.return_value.returncode = 0
    mock_subprocess_run.return_value.stdout = stdout

    config = {
        "parameters": [
            {
                "threads": [1, 2],
                "cpu-max-prime": [10000]
            }
        ]
    }
    runner = CPUBenchmarker(config)
    runner.run()

    # Ensure subprocess.run is called with the correct command
    expected_calls = [
        (['sysbench', 'cpu', '--threads=1', '--cpu-max-prime=10000', 'run'],),
        (['sysbench', 'cpu', '--threads=2', '--cpu-max-prime=10000', 'run'],)
    ]
    assert mock_subprocess_run.call_count == 2
    for call_args in expected_calls:
        mock_subprocess_run.assert_any_call(
            call_args[0], capture_output=True, text=True, check=True)

    # Ensure results contain parsed data
    print(runner.results)
    assert len(runner.results) == 2
    assert runner.results[0]['events_per_second'] == 853267.75


@patch('subprocess.run')
def test_sysbench_cpu_runner_error(mock_subprocess_run: MagicMock):
    """
    Tests the error handling of the CPUBenchmarker class by mocking subprocess.run to simulate an error.
    """
    # Mocking the return value of subprocess.run to simulate an error
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd='sysbench', stderr=stdout)

    config = {
        "parameters": [
            {
                "threads": [1],
                "cpu-max-prime": [10000]
            }
        ]
    }
    runner = CPUBenchmarker(config)
    runner.run()

    # Ensure subprocess.run is called with the correct command
    mock_subprocess_run.assert_called_once_with(
        ['sysbench', 'cpu', '--threads=1', '--cpu-max-prime=10000', 'run'],
        capture_output=True, text=True, check=True
    )

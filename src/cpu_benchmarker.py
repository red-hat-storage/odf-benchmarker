"""
This module provides a class `SysbenchCPURunner` to run sysbench CPU tests with various configurations
and parse the results. It also includes pytest test cases to validate the functionality of the class.

Classes:
    SysbenchCPURunner: A class to run sysbench CPU tests and parse the results.

Functions:
    test_sysbench_cpu_runner(mock_parser_parse, mock_subprocess_run): Tests the SysbenchCPURunner class by mocking subprocess.run to avoid actual sysbench execution.
    test_sysbench_cpu_runner_error(mock_parser_parse, mock_subprocess_run): Tests the error handling of the SysbenchCPURunner class by mocking subprocess.run to simulate an error.

"""


import subprocess
import itertools
from typing import Dict, List, Any
from sysbench_parser import SysbenchParser
import pandas as pd


class CPUBenchmarker:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the SysbenchCPURunner with the given configuration.

        Args:
            config (Dict[str, Any]): A dictionary containing parameters for the sysbench run.
        """
        self.config = config
        self.results = []  # Store parsed results
        self.parser: SysbenchParser = None

    def run(self) -> pd.DataFrame:
        """
        Executes sysbench CPU tests based on the configuration provided.
        Iterates over all combinations of thread counts and cpu-max-prime values.
        """
        parameters = self.config.get("parameters", [])
        for param_set in parameters:
            threads: List[int] = param_set.get("threads", [])
            cpu_max_primes = param_set.get("cpu-max-prime", [10000])

            # Ensure cpu-max-prime is a list for itertools.product
            if not isinstance(cpu_max_primes, list):
                cpu_max_primes = [cpu_max_primes]

            # Create combinations of threads and cpu-max-prime using itertools.product
            for thread_count, cpu_max_prime in itertools.product(threads, cpu_max_primes):
                # Construct the sysbench command
                command = [
                    "sysbench",
                    "cpu",
                    f"--threads={thread_count}",
                    f"--cpu-max-prime={cpu_max_prime}",
                    "run"
                ]

                # Run the sysbench command using subprocess
                print(
                    f"Running sysbench with {thread_count} threads and cpu-max-prime={cpu_max_prime}")
                try:
                    result = subprocess.run(
                        command, capture_output=True, text=True, check=True)
                    sysbench_output = result.stdout

                    # Parse the sysbench output
                    parsed_data = self.parse_sysbench_output(sysbench_output)
                    parsed_data.update({
                        'threads': thread_count,
                        'cpu-max-prime': cpu_max_prime
                    })
                    self.results.append(parsed_data)
                except subprocess.CalledProcessError as e:
                    print(
                        f"Error running sysbench with {thread_count} threads: {e.stderr}")
                    parsed_data = self.parse_sysbench_output(e.stderr)
                    parsed_data.update({
                        'threads': thread_count,
                        'cpu-max-prime': cpu_max_prime
                    })
                    self.results.append(parsed_data)
        return pd.DataFrame(self.results)

    def parse_sysbench_output(self, output: str) -> Dict[str, Any]:
        """
        Parses the sysbench output and returns a dictionary of relevant information.

        Args:
            output (str): The output data from sysbench command.

        Returns:
            Dict[str, Any]: A dictionary containing parsed information from the output.
        """
        self.parser = SysbenchParser(output)
        self.parser.parse_output()
        return self.parser.data
        # Placeholder for actual parsing logic

    def get_resutls_df(self) -> pd.DataFrame:
        """
        Returns the parsed results as a pandas DataFrame.
        """
        if self.parser is None:
            raise ValueError("No results to convert to DataFrame")
        return self.parser.to_dataframe()


if __name__ == "__main__":
    config = {
        "parameters": [
            {
                "threads": [1, 2, 4, 8, 16, 32, 64, 128, 256],
                "cpu-max-prime": [100000, 200000]
            }
        ]
    }
    runner = CPUBenchmarker(config)
    runner.run()
    print(runner.results)


# Pytest test cases

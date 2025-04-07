import itertools
import json
import subprocess
import pandas as pd
from typing import List, Dict, Any, Union
from sysbench_parser import SysbenchParser


class StorageBenchmarker:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the SysbenchRunner with a configuration dictionary.

        :param config: Configuration dictionary containing disks, blocksizes, workloads, threads, and flags.
        """
        self.config = config
        self.results: List[Dict[str, Union[int, float, str]]] = []

    def parse_sysbench_output(self, output: str) -> Dict[str, Union[int, float, str]]:
        """

        Parses the output from a sysbench run and returns the results as a dictionary.
        Args:
            output (str): The raw output string from the sysbench command.
        Returns:
            Dict[str, Union[int, float]]: A dictionary containing the parsed sysbench results.

        """
        parser = SysbenchParser(output)
        parser.parse_output()
        return parser.data

    def sysbench_prepare(self, disk_path: str, blocksize: str, workload: str, thread: int, file_extra_flags: str) -> None:
        """
        Run the sysbench prepare command.

        :param disk_path: Path to the disk to be tested.
        :param blocksize: Block size for the test.
        :param workload: Type of workload (e.g., sequential write, random read).
        :param thread: Number of threads to use.
        :param file_extra_flags: Extra flags for file operations.
        """
        command = [
            'sysbench',
            f'--file-total-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'prepare'
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while preparing sysbench: {e}")

    def sysbench_run(self, disk_path: str, blocksize: str, workload: str, thread: int, file_extra_flags: str) -> None:
        """
        Run the sysbench run command and parse the output.

        :param disk_path: Path to the disk to be tested.
        :param blocksize: Block size for the test.
        :param workload: Type of workload (e.g., sequential write, random read).
        :param thread: Number of threads to use.
        :param file_extra_flags: Extra flags for file operations.
        """
        command = [
            'sysbench',
            f'--file-total-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'run'
        ]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True)
            sysbench_output = result.stdout

            # Parse the sysbench output
            parsed_data = self.parse_sysbench_output(sysbench_output)
            parsed_data.update({
                'disk': disk_path,
                'blocksize': blocksize,
                'workload': workload,
                'threads': thread,
                'flags': file_extra_flags
            })

            # Append the parsed data to the results list
            self.results.append(parsed_data)

        except subprocess.CalledProcessError as e:
            print(f"Error while running sysbench: {e}")

    def sysbench_cleanup(self, disk_path: str, blocksize: str, workload: str, thread: int, file_extra_flags: str) -> None:
        """
        Run the sysbench cleanup command.

        :param disk_path: Path to the disk to be cleaned up.
        :param blocksize: Block size for the test.
        :param workload: Type of workload (e.g., sequential write, random read).
        :param thread: Number of threads to use.
        :param file_extra_flags: Extra flags for file operations.
        """
        command = [
            'sysbench',
            f'--file-total-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'cleanup'
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error while cleaning up sysbench: {e}")

    def run_all_tests(self) -> None:
        """
        Run sysbench prepare, run, and cleanup commands for all combinations of parameters.
        """
        disks = self.config['disks']
        blocksizes = self.config['blocksizes']
        workloads = self.config['workloads']
        threads = self.config['threads']
        flags = self.config['flags']

        # Iterate over all combinations of parameters
        for disk_path, blocksize, workload, thread, flag in itertools.product(disks, blocksizes, workloads, threads, flags):
            file_extra_flags = flag['file-extra-flags']

            # Run prepare command before run command
            self.sysbench_prepare(
                disk_path, blocksize, workload, thread, file_extra_flags)
            self.sysbench_run(disk_path, blocksize,
                              workload, thread, file_extra_flags)
            self.sysbench_cleanup(
                disk_path, blocksize, workload, thread, file_extra_flags)

    def get_results_dataframe(self) -> pd.DataFrame:
        """
        Convert the results to a pandas DataFrame and return it.

        :return: A pandas DataFrame containing the results of all tests.
        """
        return pd.DataFrame(self.results)

    def run(self) -> pd.DataFrame:
        """
        Run the storage benchmark tests based on the configuration provided.

        :return: A pandas DataFrame containing the results of all tests.
        """
        self.run_all_tests()
        return self.get_results_dataframe()


if __name__ == "__main__":
    # Sample JSON configuration
    data: Dict[str, Any] = {
        "disks": [
            {
                "path": "/dev/nvme2n1"
            }
        ],
        "blocksizes": ["4k", "16k", "128k", "1M", "10M", "100M"],
        "workloads": ["seqwr", "seqrd", "seqrewr", "rndwr", "rndrd", "rndrw"],
        "threads": [4, 8, 16, 32, 64],
        "flags": [
            {
                "file-extra-flags": "dsync"
            }
        ]
    }

    # Create an instance of SysbenchRunner and run all tests
    storage_benchamrker = StorageBenchmarker(data)
    storage_benchamrker.run_all_tests()

    # Get the results as a DataFrame and display it
    df = storage_benchamrker.get_results_dataframe()
    print(df)
    # Assuming you want to return the dataframe in another context, just return 'df' as needed.

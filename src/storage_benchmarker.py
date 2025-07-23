import itertools
import subprocess
import pandas as pd
import os
from typing import List, Dict, Any, Union, Optional
from sysbench_parser import SysbenchParser


class StorageBenchmarker:
    def __init__(self, config: Dict[str, Any], mount_base: Optional[str] = None) -> None:
        """
        Initialize the SysbenchRunner with a configuration dictionary.

        :param config: Configuration dictionary containing disks, blocksizes, workloads, threads, and flags.
        :param mount_base: Base directory for mounting disks (default: /mnt/benchmark)
        """
        self.config = config
        self.results: List[Dict[str, Union[int, float, str]]] = []
        self.mount_points: Dict[str, str] = {}
        self.mount_base = mount_base or "/mnt/benchmark"

    def mount_disk(self, device_path: str) -> str:
        """
        Mount a disk device to a mount point for benchmarking.
        
        :param device_path: Path to the disk device (e.g., /dev/nbd0)
        :return: Mount point path where the disk is mounted
        """
        # Create a unique mount point for this device
        device_name = os.path.basename(device_path)
        mount_point = os.path.join(self.mount_base, device_name)
        
        # Create mount point directory if it doesn't exist
        try:
            os.makedirs(mount_point, exist_ok=True)
        except OSError as e:
            print(f"Failed to create mount point directory {mount_point}: {e}")
            # Fallback to using the device directly if directory creation fails
            return device_path
        
        try:
            # Check if device is already mounted
            result = subprocess.run(['mountpoint', '-q', mount_point], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Device {device_path} is already mounted at {mount_point}")
                return mount_point
            
            # Try to mount the device
            # First, try to create a filesystem if it doesn't exist
            try:
                subprocess.run(['mkfs.ext4', '-F', device_path], 
                             capture_output=True, text=True, check=True)
                print(f"Created ext4 filesystem on {device_path}")
            except subprocess.CalledProcessError:
                # Filesystem might already exist, continue
                pass
            
            # Mount the device
            subprocess.run(['mount', device_path, mount_point], 
                         capture_output=True, text=True, check=True)
            print(f"Mounted {device_path} to {mount_point}")
            
            return mount_point
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to mount {device_path}: {e}")
            # Fallback to using the device directly if mounting fails
            return device_path

    def unmount_disk(self, mount_point: str) -> None:
        """
        Unmount a disk from its mount point.
        
        :param mount_point: Path to the mount point
        """
        try:
            if mount_point.startswith(self.mount_base):
                subprocess.run(['umount', mount_point], 
                             capture_output=True, text=True, check=True)
                print(f"Unmounted {mount_point}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to unmount {mount_point}: {e}")

    def parse_sysbench_output(self, output: str) -> Dict[str, Any]:
        """

        Parses the output from a sysbench run and returns the results as a dictionary.
        Args:
            output (str): The raw output string from the sysbench command.
        Returns:
            Dict[str, Any]: A dictionary containing the parsed sysbench results.

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
        # Get the mount point for this disk
        mount_point = self.mount_points.get(disk_path, disk_path)
        
        command = [
            'sysbench',
            f'--file-block-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'prepare'
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True, cwd=mount_point)
        except subprocess.CalledProcessError as e:
            print(f"Error while preparing sysbench: {e}")
            if e.stdout:
                print("Sysbench STDOUT:\n", e.stdout)
            if e.stderr:
                print("Sysbench STDERR:\n", e.stderr)

    def sysbench_run(self, disk_path: str, blocksize: str, workload: str, thread: int, file_extra_flags: str) -> None:
        """
        Run the sysbench run command and parse the output.

        :param disk_path: Path to the disk to be tested.
        :param blocksize: Block size for the test.
        :param workload: Type of workload (e.g., sequential write, random read).
        :param thread: Number of threads to use.
        :param file_extra_flags: Extra flags for file operations.
        """
        # Get the mount point for this disk
        mount_point = self.mount_points.get(disk_path, disk_path)
        
        command = [
            'sysbench',
            f'--file-block-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'run'
        ]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, cwd=mount_point)
            sysbench_output = result.stdout

            # Parse the sysbench output
            parsed_data = self.parse_sysbench_output(sysbench_output)
            parsed_data.update({
                'disk': disk_path,
                'mount_point': mount_point,
                'blocksize': blocksize,
                'workload': workload,
                'threads': thread,
                'flags': file_extra_flags
            })

            # Append the parsed data to the results list
            self.results.append(parsed_data)

        except subprocess.CalledProcessError as e:
            print(f"Error while running sysbench: {e}")
            if e.stdout:
                print("Sysbench STDOUT:\n", e.stdout)
            if e.stderr:
                print("Sysbench STDERR:\n", e.stderr)

    def sysbench_cleanup(self, disk_path: str, blocksize: str, workload: str, thread: int, file_extra_flags: str) -> None:
        """
        Run the sysbench cleanup command.

        :param disk_path: Path to the disk to be cleaned up.
        :param blocksize: Block size for the test.
        :param workload: Type of workload (e.g., sequential write, random read).
        :param thread: Number of threads to use.
        :param file_extra_flags: Extra flags for file operations.
        """
        # Get the mount point for this disk
        mount_point = self.mount_points.get(disk_path, disk_path)
        
        command = [
            'sysbench',
            f'--file-block-size={blocksize}',
            f'--file-test-mode={workload}',
            f'--threads={thread}',
            f'--file-extra-flags={file_extra_flags}',
            'fileio',
            'cleanup'
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True, cwd=mount_point)
        except subprocess.CalledProcessError as e:
            print(f"Error while cleaning up sysbench: {e}")
            if e.stdout:
                print("Sysbench STDOUT:\n", e.stdout)
            if e.stderr:
                print("Sysbench STDERR:\n", e.stderr)

    def run_all_tests(self) -> None:
        """
        Run sysbench prepare, run, and cleanup commands for all combinations of parameters.
        """
        disks = self.config['disks']
        blocksizes = self.config['blocksizes']
        workloads = self.config['workloads']
        threads = self.config['threads']
        flags = self.config['flags']

        # Mount all disks first
        for disk_config in disks:
            disk_path = disk_config['path']
            mount_point = self.mount_disk(disk_path)
            self.mount_points[disk_path] = mount_point

        try:
            # Iterate over all combinations of parameters
            for disk_config, blocksize, workload, thread, flag in itertools.product(disks, blocksizes, workloads, threads, flags):
                disk_path = disk_config['path']
                file_extra_flags = flag['file-extra-flags']

                # Run prepare command before run command
                self.sysbench_prepare(
                    disk_path, blocksize, workload, thread, file_extra_flags)
                self.sysbench_run(disk_path, blocksize,
                                  workload, thread, file_extra_flags)
                self.sysbench_cleanup(
                    disk_path, blocksize, workload, thread, file_extra_flags)
        finally:
            # Unmount all disks
            for disk_path, mount_point in self.mount_points.items():
                self.unmount_disk(mount_point)

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

import subprocess
import json
import time
import re
import numpy as np
import pandas as pd
from unittest import mock
import pytest
from typing import List, Dict, Any, Optional


class NetworkBenchmarker:
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the NetworkBenchmarker with the provided configuration.

        :param config: A dictionary containing benchmark configuration including interfaces, peers, threads, and workloads.
        """
        self.interfaces: List[str] = config.get("interfaces", [])
        self.peers: List[str] = config.get("peers", [])
        self.workloads: List[str] = config.get("workloads", [])
        self.threads: List[int] = config.get("threads", [1])
        self.results_df: pd.DataFrame = pd.DataFrame(
            columns=["workload", "interface", "peer", "threads", "avg_latency", "p95_latency", "bandwidth"])

    def run_iperf_benchmark(self, interface: str, peer: str, num_threads: int) -> None:
        """
        Runs the iperf3 benchmarking tool from this host to a peer with the specified number of threads.

        :param interface: Network interface to be used.
        :param peer: Peer hostname or IP address to run iperf against.
        :param num_threads: Number of parallel threads to use.
        """
        print(
            f"Running iperf3 benchmark to peer {peer} on interface {interface} with {num_threads} threads...")
        try:
            # Running iperf3 in client mode with specified number of threads
            result = subprocess.run([
                'iperf3', '-c', peer, '--bind-dev', interface, '-P', str(
                    num_threads), '-t', '10'
            ], capture_output=True, text=True)

            # Display the results
            if result.returncode == 0:
                print(
                    f"iperf3 results for peer {peer} with {num_threads} threads:")
                print(result.stdout)
                # Extract bandwidth from iperf3 output
                bandwidth_match = re.search(
                    r'\[SUM\].*?\s+(\d+(\.\d+)?)\s+(Mbits|Gbits)', result.stdout)
                bandwidth: Optional[float] = None
                if bandwidth_match:
                    bandwidth = float(bandwidth_match.group(1))
                    bandwidth_unit = bandwidth_match.group(3)
                    if bandwidth_unit == "Gbits":
                        bandwidth *= 1000  # Convert Gbits to Mbits

                # Save to dataframe
                self.results_df = pd.concat([self.results_df, pd.DataFrame([{
                    "workload": "iperf",
                    "interface": interface,
                    "peer": peer,
                    "threads": num_threads,
                    "avg_latency": None,
                    "p95_latency": None,
                    "bandwidth": bandwidth
                }])], ignore_index=True)
            else:
                print(
                    f"iperf3 failed for peer {peer} with {num_threads} threads with error:")
                print(result.stderr)
        except Exception as e:
            print(
                f"Exception occurred while running iperf3 for peer {peer} with {num_threads} threads: {str(e)}")

    def run_ping_benchmark(self, peer: str) -> None:
        """
        Runs the ping benchmarking tool from this host to a peer to measure latency.

        :param peer: Peer hostname or IP address to ping.
        """
        print(f"Running ping benchmark to peer {peer}...")
        try:
            # Running ping to measure latency
            result = subprocess.run([
                'ping', '-c', '10', peer
            ], capture_output=True, text=True)

            # Display the results
            if result.returncode == 0:
                print(f"Ping results for peer {peer}:")
                print(result.stdout)

                # Extract RTT values from ping output
                rtt_lines = re.findall(r'time=(\d+\.\d+) ms', result.stdout)
                rtt_values = [float(rtt) for rtt in rtt_lines]

                if rtt_values:
                    avg_latency = float(np.mean(rtt_values))
                    p95_latency = float(np.percentile(rtt_values, 95))
                    print(f"Average Latency: {avg_latency:.2f} ms")
                    print(f"95th Percentile Latency: {p95_latency:.2f} ms")
                    # Save to dataframe
                    self.results_df = pd.concat([self.results_df, pd.DataFrame([{
                        "workload": "ping",
                        "interface": None,
                        "peer": peer,
                        "threads": None,
                        "avg_latency": avg_latency,
                        "p95_latency": p95_latency,
                        "bandwidth": None
                    }])], ignore_index=True)
            else:
                print(f"Ping failed for peer {peer} with error:")
                print(result.stderr)
        except Exception as e:
            print(
                f"Exception occurred while running ping for peer {peer}: {str(e)}")

    def run_hping_benchmark(self, peer: str) -> None:
        """
        Runs the hping3 benchmarking tool to measure advanced latency metrics.

        :param peer: Peer hostname or IP address to hping.
        """
        print(f"Running hping3 benchmark to peer {peer}...")
        try:
            # Running hping3 to measure latency
            result = subprocess.run([
                'hping3', '-S', peer, '-p', '80', '-c', '10'
            ], capture_output=True, text=True)

            # Display the results
            if result.returncode == 0:
                print(f"hping3 results for peer {peer}:")
                print(result.stdout)

                # Extract RTT values from hping3 output
                rtt_lines = re.findall(r'rtt=(\d+\.\d+) ms', result.stdout)
                rtt_values = [float(rtt) for rtt in rtt_lines]

                if rtt_values:
                    avg_latency = float(np.mean(rtt_values))
                    p95_latency = float(np.percentile(rtt_values, 95))
                    print(f"Average Latency: {avg_latency:.2f} ms")
                    print(f"95th Percentile Latency: {p95_latency:.2f} ms")
                    # Save to dataframe
                    self.results_df = pd.concat([self.results_df, pd.DataFrame([{
                        "workload": "hping",
                        "interface": None,
                        "peer": peer,
                        "threads": None,
                        "avg_latency": avg_latency,
                        "p95_latency": p95_latency,
                        "bandwidth": None
                    }])], ignore_index=True)
            else:
                print(f"hping3 failed for peer {peer} with error:")
                print(result.stderr)
        except Exception as e:
            print(
                f"Exception occurred while running hping3 for peer {peer}: {str(e)}")

    def run(self) -> pd.DataFrame:
        """
        Executes the benchmarks based on the specified workloads and returns a dataframe containing the results.

        :return: A Pandas DataFrame containing the benchmarking results.
        """
        for interface in self.interfaces:
            for peer in self.peers:
                if "iperf" in self.workloads:
                    for num_threads in self.threads:
                        self.run_iperf_benchmark(interface, peer, num_threads)
                        # Wait a few seconds between tests to avoid overloading the network
                        time.sleep(5)
                if "ping" in self.workloads:
                    self.run_ping_benchmark(peer)
                    # Wait a few seconds between tests to avoid overloading the network
                    time.sleep(5)
                if "hping3" in self.workloads:
                    self.run_hping_benchmark(peer)
                    # Wait a few seconds between tests to avoid overloading the network
                    time.sleep(5)
        return self.results_df

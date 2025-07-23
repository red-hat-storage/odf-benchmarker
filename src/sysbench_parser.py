import re
import json
import pandas as pd
import unittest
from typing import List, Dict, Any, Union

    # Assuming you have a parser function that parses sysbench output to a dict


class SysbenchParser:
    """
    A parser for sysbench output, capable of parsing both file I/O and CPU benchmark results.
    """

    def __init__(self, text_output: str):
        """
        Initializes the SysbenchParser with the given sysbench output.

        :param text_output: The raw output from a sysbench command.
        """
        self.text_output = text_output
        self.data: Dict[str, Union[int, float]] = {}

    def parse_output(self) -> Dict[str, Union[int, float]]:
        """
        Parses the sysbench output and populates the data attribute with parsed results.

        :return: A dictionary containing parsed benchmark results.
        :raises ValueError: If the output format is unsupported.
        """
        if "File operations" in self.text_output:
            self._parse_fileio_output()
        elif "CPU speed" in self.text_output or "events per second" in self.text_output:
            self._parse_cpu_output()
        else:
            raise ValueError("Unsupported benchmark output format")
        return self.data

    def _parse_fileio_output(self) -> None:
        """
        Parses the file I/O benchmark output and populates the data attribute.
        """
        # Define regex patterns for fileio benchmark sections of interest
        patterns = {
            "reads/s": r"reads/s:\s+(\d+\.\d+)",
            "writes/s": r"writes/s:\s+(\d+\.\d+)",
            "fsyncs/s": r"fsyncs/s:\s+(\d+\.\d+)",
            "read_mib/s": r"read, MiB/s:\s+(\d+\.\d+)",
            "written_mib/s": r"written, MiB/s:\s+(\d+\.\d+)",
            "total_time": r"total time:\s+(\d+\.\d+)s",
            "total_events": r"total number of events:\s+(\d+)",
            "latency_min": r"min:\s+(\d+\.\d+)",
            "latency_avg": r"avg:\s+(\d+\.\d+)",
            "latency_max": r"max:\s+(\d+\.\d+)",
            "latency_95th": r"95th percentile:\s+(\d+\.\d+)",
            "latency_sum": r"sum:\s+(\d+\.\d+)",
            "events_avg": r"events \(avg/stddev\):\s+(\d+\.\d+)",
            "events_stddev": r"events \(avg/stddev\):\s+\d+\.\d+/([\d\.]+)",
            "execution_time_avg": r"execution time \(avg/stddev\):\s+(\d+\.\d+)",
            "execution_time_stddev": r"execution time \(avg/stddev\):\s+\d+\.\d+/([\d\.]+)"
        }

        # Extract data using regex
        for key, pattern in patterns.items():
            match = re.search(pattern, self.text_output)
            if match:
                self.data[key] = float(match.group(1)) if '.' in match.group(
                    1) else int(match.group(1))

    def _parse_cpu_output(self) -> None:
        """
        Parses the CPU benchmark output and populates the data attribute.
        """
        # Define regex patterns for cpu benchmark sections of interest
        patterns = {
            "events_per_second": r"events per second:\s+(\d+\.\d+)",
            "total_time": r"total time:\s+(\d+\.\d+)s",
            "total_events": r"total number of events:\s+(\d+)",
            "latency_min": r"min:\s+(\d+\.\d+)",
            "latency_avg": r"avg:\s+(\d+\.\d+)",
            "latency_max": r"max:\s+(\d+\.\d+)",
            "latency_95th": r"95th percentile:\s+(\d+\.\d+)",
            "latency_sum": r"sum:\s+(\d+\.\d+)"
        }

        # Extract data using regex
        for key, pattern in patterns.items():
            match = re.search(pattern, self.text_output)
            if match:
                self.data[key] = float(match.group(1)) if '.' in match.group(
                    1) else int(match.group(1))

    def to_json(self) -> str:
        """
        Converts the parsed data to JSON format.

        :return: A JSON string representation of the parsed data.
        """
        return json.dumps(self.data, indent=4)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the parsed data to a pandas DataFrame.

        :return: A pandas DataFrame containing the parsed data.
        """
        return pd.DataFrame([self.data])

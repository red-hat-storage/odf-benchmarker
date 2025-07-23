import pytest
import pandas as pd
from src.sysbench_parser import SysbenchParser

def test_parse_cpu_output_full():
    sysbench_output = """
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
    parser = SysbenchParser(sysbench_output)
    parsed_data = parser.parse_output()
    assert pytest.approx(parsed_data["events_per_second"]) == 853267.75
    assert pytest.approx(parsed_data["total_time"]) == 10.0002
    assert parsed_data["total_events"] == 8537887
    assert pytest.approx(parsed_data["latency_min"]) == 0.00
    assert pytest.approx(parsed_data["latency_avg"]) == 0.00
    assert pytest.approx(parsed_data["latency_max"]) == 0.07
    assert pytest.approx(parsed_data["latency_95th"]) == 0.00
    assert pytest.approx(parsed_data["latency_sum"]) == 9291.90

def test_parse_fileio_output_full():
    sysbench_output = """
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
    parser = SysbenchParser(sysbench_output)
    parsed_data = parser.parse_output()
    assert pytest.approx(parsed_data["writes/s"]) == 29718.09
    assert pytest.approx(parsed_data["fsyncs/s"]) == 1191.86
    assert pytest.approx(parsed_data["written_mib/s"]) == 116.09
    assert pytest.approx(parsed_data["total_time"]) == 10.0009
    assert parsed_data["total_events"] == 309103
    assert pytest.approx(parsed_data["latency_avg"]) == 0.26
    assert pytest.approx(parsed_data["latency_max"]) == 8.15
    assert pytest.approx(parsed_data["latency_sum"]) == 79932.20

def test_parse_output_unsupported():
    parser = SysbenchParser("nonsense output")
    with pytest.raises(ValueError):
        parser.parse_output()

def test_to_json_and_to_dataframe():
    sysbench_output = "CPU speed:\n    events per second: 1000.00"
    parser = SysbenchParser(sysbench_output)
    parser.parse_output()
    json_str = parser.to_json()
    assert "events_per_second" in json_str
    df = parser.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert "events_per_second" in df.columns

def test_empty_output():
    parser = SysbenchParser("")
    with pytest.raises(ValueError):
        parser.parse_output()

def test_partial_output():
    sysbench_output = "CPU speed:\n    events per second: 1234.56"
    parser = SysbenchParser(sysbench_output)
    data = parser.parse_output()
    assert data["events_per_second"] == 1234.56
    # Only one key should be present
    assert len(data) == 1 
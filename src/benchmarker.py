from network_benchmarker import NetworkBenchmarker
from cpu_benchmarker import CPUBenchmarker
from storage_benchmarker import StorageBenchmarker
from metrics_generator import generate_node_specific_metrics
import pandas as pd
import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser(
        description="Run various benchmarks on the system.")
    parser.add_argument("--resources", type=str, required=True,
                        help="Path to the configuration file.")
    parser.add_argument("--metrics", type=str,
                        default="metrics.json",
                        help="Path to the configuration file.", required=False)
    args = parser.parse_args()
    with open(args.resources) as f:
        resources = json.load(f)
    with open(args.metrics) as f:
        metrics_template = json.load(f)

    print("Running benchmarks with the following configuration:")
    print("Metrics:", metrics_template)
    print("Resources:", resources)
    node = os.environ.get("NODE_NAME", "")
    config = generate_node_specific_metrics(metrics_template, resources, node)
    cpu = CPUBenchmarker(config.get("cpu", {}))
    storage = StorageBenchmarker(config.get(
        "storage", {})) if config.get("storage", {}) else None
    network = NetworkBenchmarker(config.get("network", {}))
    df = pd.DataFrame()
    for b in [cpu, storage]:
        print("Running", b.__class__.__name__)
        if b is None:
            continue
        bdf = b.run()
        df = pd.concat([df, bdf])
    df.to_csv("results.csv", index=False)
    print(df)


if __name__ == "__main__":
    main()

# ODF Benchmarker

A comprehensive benchmarking tool for OpenShift Data Foundation (ODF) performance testing. This tool runs CPU, storage, and network benchmarks on Kubernetes nodes to evaluate system performance.

## Overview

The ODF Benchmarker is designed to run performance benchmarks on Kubernetes nodes, specifically targeting:
- **Storage Performance**: Tests disk I/O performance using sysbench on mounted disks
- **CPU Performance**: Tests CPU performance using sysbench
- **Network Performance**: Tests network performance using iperf3, ping, and hping3

## Key Features

### Storage Benchmarking
- **Disk Mounting**: Automatically mounts disk devices to `/mnt/benchmark/` directories
- **Filesystem Creation**: Creates ext4 filesystems on unmounted disks
- **Multiple Workloads**: Tests sequential read/write, random read/write, and mixed workloads
- **Configurable Parameters**: Supports various block sizes, thread counts, and I/O flags

### CPU Benchmarking
- **Prime Number Calculation**: Tests CPU performance using prime number calculations
- **Multi-threaded Testing**: Supports various thread configurations

### Network Benchmarking
- **Bandwidth Testing**: Uses iperf3 for bandwidth measurements
- **Latency Testing**: Uses ping for latency measurements
- **Stress Testing**: Uses hping3 for network stress testing

## Recent Fixes

### Issue Fixed: Local Filesystem vs Mounted Disks
**Problem**: The original implementation was running storage benchmarks on the pod's local filesystem instead of the actual mounted disks specified in `resources.json`.

**Solution**: 
1. **Disk Mounting**: Added automatic disk mounting functionality that mounts each disk device to a unique mount point
2. **Sysbench Directory**: Modified sysbench commands to use `--file-test-dir` parameter to specify the mount point
3. **Privileged Container**: Updated Kubernetes manifests to run in privileged mode with host device access
4. **Filesystem Creation**: Added automatic filesystem creation for unmounted disks

### Changes Made:
- `src/storage_benchmarker.py`: Added disk mounting and unmounting functionality
- `Dockerfile`: Added necessary tools (e2fsprogs, mount, mountpoint)
- `daemonSet.yaml` & `pod.yaml`: Added privileged mode and host device mounts
- `src/test_storage_benchmarker.py`: Updated tests to reflect new disk configuration format

## Configuration

### Resources Configuration (`resources.json`)
```json
{
  "nodes": [
    {
      "node_name": "worker-node-1",
      "disks": ["nbd0", "nbd1", "vda", "vdb"],
      "network_interfaces": ["ens3"]
    }
  ]
}
```

### Metrics Configuration (`metrics.json`)
```json
{
  "storage": {
    "blocksizes": ["4k", "16k"],
    "workloads": ["seqwr", "seqrd"],
    "threads": [4, 8],
    "flags": [{"file-extra-flags": "dsync"}]
  },
  "network": {
    "threads": [1, 4],
    "workloads": ["iperf", "ping", "hping3"]
  },
  "cpu": {
    "parameters": [
      {
        "threads": [1, 2, 4],
        "cpu-max-prime": 100000
      }
    ]
  }
}
```

## Deployment

### Using DaemonSet (Recommended)
```bash
# Create ConfigMap with resources and metrics
kubectl create configmap benchmark-metrics \
  --from-file=benchmark.json=resources.json \
  --from-file=metrics.json=src/metrics.json

# Deploy the DaemonSet
kubectl apply -f daemonSet.yaml
```

### Using Pod (Single Node)
```bash
# Create ConfigMap
kubectl create configmap benchmark-metrics \
  --from-file=metrics.json=src/metrics.json

# Deploy the Pod
kubectl apply -f pod.yaml
```

## Security Considerations

The benchmarker runs in privileged mode to:
- Access host device files (`/dev/*`)
- Mount and unmount filesystems
- Create filesystems on disk devices

**⚠️ Warning**: This requires elevated privileges and should only be used in controlled environments.

## Building the Container

```bash
# Build the Docker image
docker build -t odf-benchmarker:latest .

# Push to registry (replace with your registry)
docker tag odf-benchmarker:latest quay.io/myathnal/odf-benchmarker:latest
docker push quay.io/myathnal/odf-benchmarker:latest
```

## Running Tests

### Local Testing
```bash
# Run the test script
python test_mount_fix.py

# Run individual benchmarks
python src/benchmarker.py --resources resources.json --metrics src/metrics.json
```

### Kubernetes Testing
```bash
# Check pod status
kubectl get pods -l app=odf-preinstall-benchmark

# View logs
kubectl logs -l app=odf-preinstall-benchmark

# Get results
kubectl exec -it <pod-name> -- cat results.csv
```

## Results

Benchmark results are saved to `results.csv` in the container and include:
- **Storage**: Throughput, latency, I/O operations per second
- **CPU**: Events per second, execution time
- **Network**: Bandwidth, latency, packet loss

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure the container runs in privileged mode
2. **Device Not Found**: Verify disk devices exist in `/dev/` on the host
3. **Mount Failed**: Check if disk has existing filesystem or is in use
4. **Sysbench Not Found**: Ensure sysbench is installed in the container

### Debug Commands
```bash
# Check mounted filesystems
kubectl exec -it <pod-name> -- mount

# List available devices
kubectl exec -it <pod-name> -- ls -la /dev/

# Check sysbench installation
kubectl exec -it <pod-name> -- sysbench --version
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

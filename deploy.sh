#!/bin/bash

# This script deploys the ODF Benchmarker DaemonSet to a Kubernetes cluster.
#
# It performs the following steps:
# 1. Sets the path to the resources.json file, defaulting to './resources.json'.
# 2. Deletes any pre-existing 'benchmark-config' ConfigMap.
# 3. Creates a new ConfigMap from the specified resources.json and the default src/metrics.json.
# 4. Applies the DaemonSet from the official GitHub repository.
#
# Usage:
#   ./deploy.sh [path/to/your/resources.json]

set -e

# --- Configuration ---
# Use the first argument as the resources file path, or default to 'resources.json'
RESOURCES_FILE="${1:-resources.json}"
METRICS_FILE="src/metrics.json"
CONFIG_MAP_NAME="benchmark-config"
DAEMONSET_URL="https://raw.githubusercontent.com/red-hat-storage/odf-benchmarker/main/daemonSet.yaml"

# --- Pre-flight Checks ---
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl command not found. Please install it and ensure it's in your PATH."
    exit 1
fi

if [ ! -f "$RESOURCES_FILE" ]; then
    echo "❌ Resources file not found at '$RESOURCES_FILE'. Please provide a valid path."
    exit 1
fi

echo "🚀 Starting ODF Benchmarker deployment..."
echo "------------------------------------------"
echo "Resources file:  $RESOURCES_FILE"
echo "ConfigMap name:  $CONFIG_MAP_NAME"
echo "DaemonSet URL:   $DAEMONSET_URL"
echo "------------------------------------------"


# --- Deployment Steps ---

# 1. Delete existing ConfigMap if it exists, ignoring errors if it doesn't.
echo "🔄 Step 1: Deleting existing ConfigMap (if any)..."
kubectl delete configmap "$CONFIG_MAP_NAME" --ignore-not-found=true

# 2. Create the ConfigMap from the local resources and metrics files.
# The DaemonSet expects keys 'resources.json' and 'metrics.json'.
echo "📦 Step 2: Creating new ConfigMap '$CONFIG_MAP_NAME'..."
kubectl create configmap "$CONFIG_MAP_NAME" \
  --from-file="resources.json=$RESOURCES_FILE" \
echo "✅ ConfigMap created successfully."

# 3. Apply the DaemonSet from the specified URL.
echo "🛰️ Step 3: Applying the DaemonSet from GitHub..."
kubectl apply -f "$DAEMONSET_URL"

echo "------------------------------------------"
echo "✅ Deployment initiated successfully!"
echo "Use 'kubectl get pods -l app=odf-preinstall-benchmark -w' to monitor the benchmark pods." 
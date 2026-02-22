#!/bin/bash
set -e

LAYER_DIR="python_layer"
PYTHON_DIR="$LAYER_DIR/python/lib/python3.14/site-packages"

rm -rf "$LAYER_DIR"
mkdir -p "$PYTHON_DIR"

pip install -r ../requirements.txt -t "$PYTHON_DIR" --upgrade

rm -f lambda_layer.zip
cd "$LAYER_DIR"
zip -r ../lambda_layer.zip .
cd ..

echo "Layer built: lambda_layer.zip"

data "archive_file" "quota_collector_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda/quota-collector.zip"
}

data "archive_file" "reporting_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda/reporting.zip"
}

# Generate the build script for Lambda Layer
resource "local_file" "build_layer_script" {
  filename = "${path.module}/build_layer.sh"
  content  = <<-EOT
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
EOT

  file_permission = "0755"
}

# Build the Lambda Layer with Python dependencies
resource "null_resource" "build_layer" {
  depends_on = [local_file.build_layer_script]
  
  triggers = {
    requirements = filemd5("${path.module}/../requirements.txt")
  }

  provisioner "local-exec" {
    command     = "bash build_layer.sh"
    working_dir = path.module
  }
}

data "archive_file" "lambda_layer" {
  depends_on = [null_resource.build_layer]
  
  type        = "zip"
  source_dir  = "${path.module}/python_layer"
  output_path = "${path.module}/lambda_layer.zip"
}

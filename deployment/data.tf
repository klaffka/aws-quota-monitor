data "archive_file" "quota_collector_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda/quota-collector.zip"
  excludes    = ["**/__pycache__/**", "**/*.pyc"]
}

data "archive_file" "reporting_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda/reporting.zip"
  excludes    = ["**/__pycache__/**", "**/*.pyc"]
}

resource "null_resource" "build_layer" {
  triggers = {
    requirements = filesha256("${path.module}/../requirements.txt")
    script       = filesha256("${path.module}/build_layer.sh")
    platform     = "python3.14-manylinux2014-x86_64"
  }
  provisioner "local-exec" {
    command     = "bash build_layer.sh"
    working_dir = path.module
  }
}

data "local_file" "lambda_layer" {
  depends_on = [null_resource.build_layer]
  filename   = "${path.module}/lambda_layer.zip"
}

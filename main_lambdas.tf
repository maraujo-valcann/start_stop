data "archive_file" "function1_code" {
  type        = "zip"
  source_file = "function1_code.py"
  output_path = "function1.zip"
}

data "archive_file" "function2_code" {
  type        = "zip"
  source_file = "function2_code.py"
  output_path = "function2.zip"
}

provider "aws" {
  region = var.region
}
locals {
  test_payload = jsondecode(file("test_payload.json"))
}

resource "aws_lambda_function" "function1" {
  function_name = var.start_resources_function
  handler       = "function1_code.lambda_handler"
  runtime       = "python3.8"
  role              = aws_iam_role.start_stop_lambda_role.arn
  filename         = data.archive_file.function1_code.output_path
  source_code_hash = filebase64sha256(data.archive_file.function1_code.output_path)
  timeout         = 900

  environment {
    variables = {
      REGION = var.region
      TEST_PAYLOAD = jsonencode(local.test_payload)
    }
  }
}

resource "aws_lambda_function" "function2" {
  function_name = var.stop_resources_function
  handler       = "function2_code.lambda_handler"
  runtime       = "python3.8"
  role              = aws_iam_role.start_stop_lambda_role.arn
  filename         = data.archive_file.function2_code.output_path
  source_code_hash = filebase64sha256(data.archive_file.function2_code.output_path)
  timeout         = 900

  environment {
    variables = {
      REGION = var.region
      TEST_PAYLOAD = jsonencode(local.test_payload)
    }
  }
}
resource "aws_cloudwatch_event_rule" "lambda_trigger" {
  name                = "lambda_trigger"
  description         = "Trigger Lambda functions"
  schedule_expression = "rate(5 minutes)"
}
resource "aws_lambda_permission" "lambda_trigger_permission" {
  statement_id  = "AllowCloudWatchEvent"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function1.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}
resource "aws_lambda_permission" "lambda_trigger_permission2" {
  statement_id  = "AllowCloudWatchEvent2"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}
resource "aws_lambda_permission" "function1_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function1.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}

resource "aws_lambda_permission" "function2_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.function2.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}

resource "aws_cloudwatch_event_target" "function1_target" {
  rule      = aws_cloudwatch_event_rule.lambda_trigger.name
  arn       = aws_lambda_function.function1.arn
}

resource "aws_cloudwatch_event_target" "function2_target" {
  rule      = aws_cloudwatch_event_rule.lambda_trigger.name
  arn       = aws_lambda_function.function2.arn
}

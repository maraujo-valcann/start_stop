#role com ec2 full acess e cloudwatch full acess
#role do ec2 deve ter read acess e start stop instance
#role do cloudwatch deve ter read acess e enable e disable alarm
resource "aws_iam_role" "start_stop_lambda_role" {
  name = "start_stop_lambda_role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ec2_read_start_stop_policy" {
  name        = "ec2_read_start_stop_policy"
  description = "Policy with read and start/stop access to EC2 instances"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "EC2ReadAccess",
        "Effect": "Allow",
        "Action": [
          "ec2:Describe*",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ],
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iam_policy" "cloudwatch_read_enable_disable_alarm_policy" {
  name        = "cloudwatch_read_enable_disable_alarm_policy"
  description = "Policy with read and enable/disable alarm access to CloudWatch resources"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "CloudWatchReadAccess",
        "Effect": "Allow",
        "Action": [
          "cloudwatch:Describe*",
          "cloudwatch:Get*",
          "cloudwatch:EnableAlarmActions",
          "cloudwatch:DisableAlarmActions"
        ],
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_read_start_stop_attachment" {
  role       = aws_iam_role.start_stop_lambda_role.name
  policy_arn = aws_iam_policy.ec2_read_start_stop_policy.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_read_enable_disable_alarm_attachment" {
  role       = aws_iam_role.start_stop_lambda_role.name
  policy_arn = aws_iam_policy.cloudwatch_read_enable_disable_alarm_policy.arn
}
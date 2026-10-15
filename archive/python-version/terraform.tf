# Legacy infrastructure retained only so the teardown workflow can destroy it.
# Do not apply this configuration to deploy new resources.

provider "aws" {
  region = "us-east-1" # Required for ACM with API Gateway
}

resource "aws_s3_object" "lambda_package" {
  bucket = "sigfriedjk-quickquiz-generator-bundles"  # Use the static bucket name
  key    = "quiz-lambda.zip"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "lambda_logs" {
  name       = "lambda_logs"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "quiz_lambda" {
  function_name    = "quiz_lambda"
  role            = aws_iam_role.lambda_role.arn
  runtime         = "python3.12"
  handler         = "lambda_function.lambda_handler"
  s3_bucket       = "sigfriedjk-quickquiz-generator-bundles"  # Use the static bucket name
  s3_key          = aws_s3_object.lambda_package.key
  timeout         = 10

  # Setting environment variables
  environment {
    variables = {
      PASSWORD = var.lambda_password
    }
  }
}

variable "lambda_password" {
  description = "Password for accessing the Lambda function"
  type        = string
  sensitive   = true
}

resource "aws_apigatewayv2_api" "quiz_api" {
  name          = "quiz-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id             = aws_apigatewayv2_api.quiz_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.quiz_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "quiz_route" {
  api_id    = aws_apigatewayv2_api.quiz_api.id
  route_key = "GET /quiz"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.quiz_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.quiz_api.execution_arn}/*/*"
}

resource "aws_acm_certificate" "cert" {
  domain_name       = "math.thekingfamily.email"
  validation_method = "DNS"
}

resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = "Z0724761289BFRC8HX0Q3"
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "cert_validation" {
  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}

resource "aws_apigatewayv2_domain_name" "custom_domain" {
  domain_name = "math.thekingfamily.email"
  domain_name_configuration {
    certificate_arn = aws_acm_certificate.cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api_mapping" "custom_mapping" {
  api_id      = aws_apigatewayv2_api.quiz_api.id
  domain_name = aws_apigatewayv2_domain_name.custom_domain.id
  stage       = aws_apigatewayv2_stage.default.id 
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.quiz_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_route53_record" "custom_api_dns" {
  zone_id = "Z0724761289BFRC8HX0Q3"
  name    = "math.thekingfamily.email"
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.custom_domain.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.custom_domain.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

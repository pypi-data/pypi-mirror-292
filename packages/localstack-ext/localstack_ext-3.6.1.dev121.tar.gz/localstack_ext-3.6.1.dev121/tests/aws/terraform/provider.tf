provider "aws" {
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  s3_use_path_style           = true

  endpoints {
    apigateway = "http://localhost:4566"
    appsync    = "http://localhost:4566"
    cognitoidentity = "http://localhost:4566"
    cognitoidp = "http://localhost:4566"
    ec2        = "http://localhost:4566"
    emr        = "http://localhost:4566"
    glacier    = "http://localhost:4566"
    iam        = "http://localhost:4566"
    lambda     = "http://localhost:4566"
    rds        = "http://localhost:4566"
    route53    = "http://localhost:4566"
    s3         = "http://localhost:4566"
    sqs        = "http://localhost:4566"
    sts        = "http://localhost:4566"
  }
}

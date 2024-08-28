
resource "aws_appsync_graphql_api" "example" {
  authentication_type = "AMAZON_COGNITO_USER_POOLS"
  name                = "tf-test-1634"

  user_pool_config {
    aws_region     = "us-east-1"
    default_action = "DENY"
    user_pool_id   = "pool123"
  }

  schema = <<EOF
schema {
    query: Query
}
type Query {
  test: Int
}
EOF
}

resource "aws_rds_cluster_parameter_group" "default" {
  name        = "test-pg-1"
  description = "DB cluster parameter group"
  family      = "aurora-mysql5.7"
}

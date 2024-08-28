resource "aws_glacier_vault" "my_archive" {
  name = "test-vault-73240"
  tags = {
    "VaultPurpose" = "Archive"
  }
}

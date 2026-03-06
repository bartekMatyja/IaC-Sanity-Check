resource "aws_s3_bucket" "test_bucket" {
  bucket = "test-checkov-scan-bucket-demo"
  acl    = "public-read"
}

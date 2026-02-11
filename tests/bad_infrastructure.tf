provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "bad_bucket" {
  bucket = "my-bad-bucket"
  acl    = "public-read"  # Non-compliant: Public ACL

  logging {
      # Missing target_bucket
  }
}

resource "aws_security_group" "bad_sg" {
  name        = "allow_all"
  description = "Allow all inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Non-compliant: Open directly to the internet
  }
}

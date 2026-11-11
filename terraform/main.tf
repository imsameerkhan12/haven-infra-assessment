# B0 — The `count` trap
#
# Each landlord account gets a dedicated S3 bucket for their media, addressed by POSITION in
# var.landlord_accounts. This is the setup the assignment asks you to reason about: what happens
# to `terraform plan` when an account in the middle of the list is removed?
#
# Try it: this directory ships with a `terraform.tfstate` already seeded with all 4 buckets, so
# you don't need a real AWS account or `terraform apply` to see this. Remove "la-002" from
# variables.tf's default list, then run:
#
#   terraform plan -refresh=false
#
# The -refresh=false matters: a plain `terraform plan` tries to refresh each resource against
# real AWS first, the dummy credentials get a 403, and Terraform quietly drops the "missing"
# resource from state and plans a fresh create instead — which hides the bug entirely. Skipping
# the refresh diffs your config directly against the seeded state, which is what shows the real
# destroy/recreate cascade.

#
# FIX: key each bucket by its landlord account ID (stable identity) instead of list position.
# Removing an account now plans exactly one destroy — that account's bucket — and nothing else.

resource "aws_s3_bucket" "landlord_media" {
  for_each = toset(var.landlord_accounts)
  bucket   = "haven-media-${each.key}"

  tags = {
    landlord_account_id = each.key
  }
}

# One-time state migration from the old count indexes to the new for_each keys, so the
# switch itself doesn't destroy/recreate anything. Index -> ID mapping comes from the seeded
# terraform.tfstate (provisioning order). Safe to delete once every environment has applied it.
moved {
  from = aws_s3_bucket.landlord_media[0]
  to   = aws_s3_bucket.landlord_media["la-001"]
}

moved {
  from = aws_s3_bucket.landlord_media[1]
  to   = aws_s3_bucket.landlord_media["la-002"]
}

moved {
  from = aws_s3_bucket.landlord_media[2]
  to   = aws_s3_bucket.landlord_media["la-003"]
}

moved {
  from = aws_s3_bucket.landlord_media[3]
  to   = aws_s3_bucket.landlord_media["la-004"]
}

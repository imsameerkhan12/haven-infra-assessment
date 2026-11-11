# B1 — The Glacier cost gotcha
#
# Sold listings' photos archive to Glacier 30 days after upload, to cut storage cost. Separately
# (not modeled in Terraform — it's an application-level flow), a seller can request deletion of
# their listing data, which must happen within 30 days of the request.
#
# Reason through: a photo archives to Glacier on day 30. The seller requests deletion on day 40.
# You delete it immediately. What does that actually cost, given Glacier's minimum storage
# duration, and what would you change here?

resource "aws_s3_bucket" "listing_media" {
  bucket = "haven-listing-media"
}

# REDESIGN (see B1.md):
#   - The original rule had no filter, so it archived EVERY photo, including active listings,
#     not just sold ones.
#   - GLACIER (Flexible Retrieval) has a 90-day minimum storage duration. An object deleted on
#     day 40 (10 days after archival) is still billed for the remaining 80 days.
#   - Sold-listing photos are exactly the population most likely to get a deletion request soon
#     after sale, so they go to INTELLIGENT_TIERING instead. It has no minimum storage duration,
#     no early-delete fee and no retrieval fee, and it still steps cold objects down to
#     Infrequent Access (30d) and Archive Instant Access (90d) on its own.
#   - Only objects that survive well past the deletion-request window go to a true Glacier
#     class, so the 90-day minimum is rarely triggered by a deletion.
#   - Objects under 128 KB are excluded. They're never auto-tiered in Intelligent-Tiering, and in
#     Glacier the ~40 KB per-object overhead plus per-object transition fees outweigh the savings.
#
# Requires the app to tag photos `listing_status = sold` when a listing sells (PutObjectTagging).
# Lifecycle `days` count from object creation (upload), not from when the tag was applied.

locals {
  sold_photo_min_bytes = 131072 # 128 KB
}

resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
  bucket = aws_s3_bucket.listing_media.id

  rule {
    id     = "tier-sold-listing-photos"
    status = "Enabled"

    filter {
      and {
        object_size_greater_than = local.sold_photo_min_bytes
        tags = {
          listing_status = "sold"
        }
      }
    }

    # 30 days after upload, same point as the original Glacier transition, but into a class
    # with no minimum duration, so an early deletion costs nothing extra.
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }

    # Deep, cheap archive only once deletion requests have mostly stopped. Tune this from real
    # deletion-request data (the 90-day minimum then mostly overlaps time the object would have
    # stayed anyway).
    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }

  # If versioning is ever enabled, a "delete" only adds a delete marker and the archived bytes
  # keep billing as a noncurrent version. That breaks both the budget and the 30-day deletion
  # requirement. Purge noncurrent versions promptly.
  rule {
    id     = "purge-noncurrent-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 1
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

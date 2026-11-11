# Terminal log

Captured output from this machine (Windows 10, PowerShell). Raw files are in `logs/`.

## 1. Setup (python, terraform, venv, pip install, pytest)

```powershell
> python --version; terraform -version; python -m venv .venv; .venv\Scripts\python -m pip install -r requirements.txt; .venv\Scripts\python -m pytest --version

Python 3.14.6
Terraform v1.16.6
on windows_amd64

Your version of Terraform is out of date! The latest version
is 1.17.1. You can update by downloading from https://developer.hashicorp.com/terraform/install

[notice] A new release of pip is available: 26.1.2 -> 26.3
[notice] To update, run: F:\Ajackus_Assignment\haven-infra-assessment\.venv\Scripts\python.exe -m pip install --upgrade pip
pytest 9.2.0
```

## 2. terraform init

```powershell
> cd terraform; terraform init

Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.100.0...
- Installed hashicorp/aws v5.100.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

## 3. B0 - baseline plan (all 4 accounts, original count)

```powershell
> terraform plan -refresh=false


Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "archive-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + transition {
              + days          = 30
              + storage_class = "GLACIER"
            }
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Warning: Invalid Attribute Combination

  with aws_s3_bucket_lifecycle_configuration.listing_media_archive,
  on lifecycle.tf line 18, in resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive":
  18:   rule {

No attribute specified when one (and only one) of
[rule[0].filter,rule[0].prefix] is required

This will be an error in a future version of the provider

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
```

## 4. B0 - la-002 removed with count (the bug)

```powershell
> # variables.tf: remove la-002
terraform plan -refresh=false


Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create
  - destroy
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # aws_s3_bucket.landlord_media[1] must be replaced
-/+ resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      ~ bucket                      = "haven-media-la-002" -> "haven-media-la-003" # forces replacement
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      ~ id                          = "haven-media-la-002" -> (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      ~ tags                        = {
          ~ "landlord_account_id" = "la-002" -> "la-003"
        }
      ~ tags_all                    = {
          ~ "landlord_account_id" = "la-002" -> "la-003"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      ~ cors_rule (known after apply)

      ~ grant (known after apply)

      ~ lifecycle_rule (known after apply)

      ~ logging (known after apply)

      ~ object_lock_configuration (known after apply)

      ~ replication_configuration (known after apply)

      ~ server_side_encryption_configuration (known after apply)

      ~ versioning (known after apply)

      ~ website (known after apply)
    }

  # aws_s3_bucket.landlord_media[2] must be replaced
-/+ resource "aws_s3_bucket" "landlord_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      ~ bucket                      = "haven-media-la-003" -> "haven-media-la-004" # forces replacement
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      ~ id                          = "haven-media-la-003" -> (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      ~ tags                        = {
          ~ "landlord_account_id" = "la-003" -> "la-004"
        }
      ~ tags_all                    = {
          ~ "landlord_account_id" = "la-003" -> "la-004"
        }
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      ~ cors_rule (known after apply)

      ~ grant (known after apply)

      ~ lifecycle_rule (known after apply)

      ~ logging (known after apply)

      ~ object_lock_configuration (known after apply)

      ~ replication_configuration (known after apply)

      ~ server_side_encryption_configuration (known after apply)

      ~ versioning (known after apply)

      ~ website (known after apply)
    }

  # aws_s3_bucket.landlord_media[3] will be destroyed
  # (because index [3] is out of range for count)
  - resource "aws_s3_bucket" "landlord_media" {
      - bucket   = "haven-media-la-004" -> null
      - id       = "haven-media-la-004" -> null
      - tags     = {
          - "landlord_account_id" = "la-004"
        } -> null
      - tags_all = {
          - "landlord_account_id" = "la-004"
        } -> null
    }

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "archive-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + transition {
              + days          = 30
              + storage_class = "GLACIER"
            }
        }
    }

Plan: 4 to add, 0 to change, 3 to destroy.

Warning: Invalid Attribute Combination

  with aws_s3_bucket_lifecycle_configuration.listing_media_archive,
  on lifecycle.tf line 18, in resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive":
  18:   rule {

No attribute specified when one (and only one) of
[rule[0].filter,rule[0].prefix] is required

This will be an error in a future version of the provider

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
```

## 5. B0 - la-002 removed with for_each + moved (the fix)

```powershell
> terraform plan -refresh=false


Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create
  - destroy

Terraform will perform the following actions:

  # aws_s3_bucket.landlord_media[0] has moved to aws_s3_bucket.landlord_media["la-001"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-001"
        tags     = {
            "landlord_account_id" = "la-001"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media["la-002"] will be destroyed
  # (because key ["la-002"] is not in for_each map)
  # (moved from aws_s3_bucket.landlord_media[1])
  - resource "aws_s3_bucket" "landlord_media" {
      - bucket   = "haven-media-la-002" -> null
      - id       = "haven-media-la-002" -> null
      - tags     = {
          - "landlord_account_id" = "la-002"
        } -> null
      - tags_all = {
          - "landlord_account_id" = "la-002"
        } -> null
    }

  # aws_s3_bucket.landlord_media[2] has moved to aws_s3_bucket.landlord_media["la-003"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-003"
        tags     = {
            "landlord_account_id" = "la-003"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[3] has moved to aws_s3_bucket.landlord_media["la-004"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-004"
        tags     = {
            "landlord_account_id" = "la-004"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "archive-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + transition {
              + days          = 30
              + storage_class = "GLACIER"
            }
        }
    }

Plan: 2 to add, 0 to change, 1 to destroy.

Warning: Invalid Attribute Combination

  with aws_s3_bucket_lifecycle_configuration.listing_media_archive,
  on lifecycle.tf line 18, in resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive":
  18:   rule {

No attribute specified when one (and only one) of
[rule[0].filter,rule[0].prefix] is required

This will be an error in a future version of the provider

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
```

## 6. B0 - all 4 accounts with for_each + moved (migration is zero-destroy)

```powershell
> git checkout -- variables.tf; terraform plan -refresh=false


Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.landlord_media[0] has moved to aws_s3_bucket.landlord_media["la-001"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-001"
        tags     = {
            "landlord_account_id" = "la-001"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[1] has moved to aws_s3_bucket.landlord_media["la-002"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-002"
        tags     = {
            "landlord_account_id" = "la-002"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[2] has moved to aws_s3_bucket.landlord_media["la-003"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-003"
        tags     = {
            "landlord_account_id" = "la-003"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[3] has moved to aws_s3_bucket.landlord_media["la-004"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-004"
        tags     = {
            "landlord_account_id" = "la-004"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "archive-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + transition {
              + days          = 30
              + storage_class = "GLACIER"
            }
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Warning: Invalid Attribute Combination

  with aws_s3_bucket_lifecycle_configuration.listing_media_archive,
  on lifecycle.tf line 18, in resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive":
  18:   rule {

No attribute specified when one (and only one) of
[rule[0].filter,rule[0].prefix] is required

This will be an error in a future version of the provider

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
```

## 7. B1 - redesigned lifecycle plan

```powershell
> terraform fmt -check -recursive
fmt exit code: 0
> terraform validate
Success! The configuration is valid.

> terraform plan -refresh=false


Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # aws_s3_bucket.landlord_media[0] has moved to aws_s3_bucket.landlord_media["la-001"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-001"
        tags     = {
            "landlord_account_id" = "la-001"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[1] has moved to aws_s3_bucket.landlord_media["la-002"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-002"
        tags     = {
            "landlord_account_id" = "la-002"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[2] has moved to aws_s3_bucket.landlord_media["la-003"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-003"
        tags     = {
            "landlord_account_id" = "la-003"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.landlord_media[3] has moved to aws_s3_bucket.landlord_media["la-004"]
    resource "aws_s3_bucket" "landlord_media" {
        id       = "haven-media-la-004"
        tags     = {
            "landlord_account_id" = "la-004"
        }
        # (2 unchanged attributes hidden)
    }

  # aws_s3_bucket.listing_media will be created
  + resource "aws_s3_bucket" "listing_media" {
      + acceleration_status         = (known after apply)
      + acl                         = (known after apply)
      + arn                         = (known after apply)
      + bucket                      = "haven-listing-media"
      + bucket_domain_name          = (known after apply)
      + bucket_prefix               = (known after apply)
      + bucket_regional_domain_name = (known after apply)
      + force_destroy               = false
      + hosted_zone_id              = (known after apply)
      + id                          = (known after apply)
      + object_lock_enabled         = (known after apply)
      + policy                      = (known after apply)
      + region                      = (known after apply)
      + request_payer               = (known after apply)
      + tags_all                    = (known after apply)
      + website_domain              = (known after apply)
      + website_endpoint            = (known after apply)

      + cors_rule (known after apply)

      + grant (known after apply)

      + lifecycle_rule (known after apply)

      + logging (known after apply)

      + object_lock_configuration (known after apply)

      + replication_configuration (known after apply)

      + server_side_encryption_configuration (known after apply)

      + versioning (known after apply)

      + website (known after apply)
    }

  # aws_s3_bucket_lifecycle_configuration.listing_media_archive will be created
  + resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
      + bucket                                 = (known after apply)
      + expected_bucket_owner                  = (known after apply)
      + id                                     = (known after apply)
      + transition_default_minimum_object_size = "all_storage_classes_128K"

      + rule {
          + id     = "tier-sold-listing-photos"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + filter {
              + and {
                  + object_size_greater_than = 131072
                  + object_size_less_than    = 0
                  + tags                     = {
                      + "listing_status" = "sold"
                    }
                    # (1 unchanged attribute hidden)
                }
            }

          + transition {
              + days          = 180
              + storage_class = "GLACIER"
            }
          + transition {
              + days          = 30
              + storage_class = "INTELLIGENT_TIERING"
            }
        }
      + rule {
          + id     = "purge-noncurrent-versions"
          + status = "Enabled"
            # (1 unchanged attribute hidden)

          + abort_incomplete_multipart_upload {
              + days_after_initiation = 7
            }

          + filter {
                # (1 unchanged attribute hidden)
            }

          + noncurrent_version_expiration {
              + noncurrent_days = 1
            }
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
```

## 8. B2 - mutation check proving the fixed assertion bites (no-op temporarily counted, then reverted)

```powershell
> # CHECKED_ACTIONS temporarily = {create, update, no-op}
pytest tests/test_cost_tag_check.py -q -k noop_and_delete


>           assert address not in out
E           AssertionError: assert 'aws_s3_buck...rchive_media' not in 'FAIL: 3 of ...ting_media\n'
tests\test_cost_tag_check.py:67: AssertionError
FAILED tests/test_cost_tag_check.py::test_fixture_noop_and_delete_entries_are_ignored_without_crashing
1 failed, 11 deselected in 0.17s
```

## 9. B2 test run 1 - access control

```powershell
> pytest tests/test_access_control.py -v

============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0 -- F:\Ajackus_Assignment\haven-infra-assessment\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: F:\Ajackus_Assignment\haven-infra-assessment
collecting ... collected 10 items

tests/test_access_control.py::test_pm_001_denied_cross_account_report PASSED [ 10%]
tests/test_access_control.py::test_pm_001_allowed_own_account_report PASSED [ 20%]
tests/test_access_control.py::test_access_matrix_is_symmetric[pm-001-rep-001-True] PASSED [ 30%]
tests/test_access_control.py::test_access_matrix_is_symmetric[pm-001-rep-002-False] PASSED [ 40%]
tests/test_access_control.py::test_access_matrix_is_symmetric[pm-002-rep-002-True] PASSED [ 50%]
tests/test_access_control.py::test_access_matrix_is_symmetric[pm-002-rep-001-False] PASSED [ 60%]
tests/test_access_control.py::test_fails_closed_when_tenant_missing PASSED [ 70%]
tests/test_access_control.py::test_fails_closed_when_property_missing PASSED [ 80%]
tests/test_access_control.py::test_fails_closed_when_tenant_id_is_ambiguous PASSED [ 90%]
tests/test_access_control.py::test_fails_closed_when_property_has_no_landlord_account PASSED [100%]

============================= 10 passed in 0.11s ==============================
```

## 10. B2 test run 2 - cost tag check

```powershell
> pytest tests/test_cost_tag_check.py -v

============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0 -- F:\Ajackus_Assignment\haven-infra-assessment\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: F:\Ajackus_Assignment\haven-infra-assessment
collecting ... collected 12 items

tests/test_cost_tag_check.py::test_fixture_flags_exactly_the_untagged_resources PASSED [  8%]
tests/test_cost_tag_check.py::test_fixture_passes_resources_that_carry_landlord_account_id PASSED [ 16%]
tests/test_cost_tag_check.py::test_tenant_id_tag_is_not_a_substitute_for_landlord_account_id PASSED [ 25%]
tests/test_cost_tag_check.py::test_fixture_noop_and_delete_entries_are_ignored_without_crashing PASSED [ 33%]
tests/test_cost_tag_check.py::test_running_twice_gives_identical_output_and_exit_code PASSED [ 41%]
tests/test_cost_tag_check.py::test_duplicate_address_in_one_plan_is_reported_once PASSED [ 50%]
tests/test_cost_tag_check.py::test_output_is_independent_of_input_order PASSED [ 58%]
tests/test_cost_tag_check.py::test_all_tagged_plan_passes PASSED         [ 66%]
tests/test_cost_tag_check.py::test_replace_action_is_checked PASSED      [ 75%]
tests/test_cost_tag_check.py::test_blank_or_null_tag_value_counts_as_missing PASSED [ 83%]
tests/test_cost_tag_check.py::test_tag_inherited_via_default_tags_in_tags_all_passes PASSED [ 91%]
tests/test_cost_tag_check.py::test_unreadable_plan_fails_closed PASSED   [100%]

============================= 12 passed in 0.24s ==============================
```

## 11. Cost-tag check, run 1

```powershell
> python scripts/cost_tag_check.py fixtures/plan.json; echo exit code: $LASTEXITCODE

FAIL: 2 of 4 resource(s) being created/updated are missing required tag 'landlord_account_id':
  - aws_lambda_function.mls_feed_sync
  - aws_s3_bucket.listing_media
exit code: 1
```

## 12. Cost-tag check, run 2 (idempotency)

```powershell
> python scripts/cost_tag_check.py fixtures/plan.json; echo exit code: $LASTEXITCODE

FAIL: 2 of 4 resource(s) being created/updated are missing required tag 'landlord_account_id':
  - aws_lambda_function.mls_feed_sync
  - aws_s3_bucket.listing_media
exit code: 1
```

## 13. Idempotency proof

```powershell
> (Get-FileHash logs\11_run1.txt, logs\12_run2.txt -Algorithm SHA256).Hash
4314E8B3465DF752CFE8A7C6137CD56D5337BB54FC447BA4313B1085A784EB71
4314E8B3465DF752CFE8A7C6137CD56D5337BB54FC447BA4313B1085A784EB71
```

Both runs: identical output, identical exit code (1, because the fixture really contains 2 untagged resources), identical SHA-256. Run 1 = run 2: **True**.

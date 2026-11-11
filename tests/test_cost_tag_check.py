"""
Write tests here proving:
  1. Happy path: running the check against fixtures/plan.json correctly flags the resources
     missing `landlord_account_id` (listing_media, mls_feed_sync) and passes the ones that
     have it (landlord_media[0], screening_report_export). The fixture also has a "no-op"
     entry and a "delete" entry with no `after` block at all — neither should appear in the
     output or crash the check.
  2. Idempotency: running the check twice against the same plan file produces the same
     result both times, with no duplicated output.

check_plan() takes a file path, not a dict — for a case that needs its own plan contents
instead of the shared fixture, write one with pytest's `tmp_path` rather than editing
fixtures/plan.json. You don't need to shell out to the real script for every case.
"""
import json
from pathlib import Path

from scripts.cost_tag_check import check_plan

FIXTURE = str(Path(__file__).resolve().parent.parent / "fixtures" / "plan.json")

FLAGGED = ["aws_lambda_function.mls_feed_sync", "aws_s3_bucket.listing_media"]
PASSING = ["aws_s3_bucket.landlord_media[0]", "aws_lambda_function.screening_report_export"]
SKIPPED = ["aws_s3_bucket.archive_media", "aws_s3_bucket.decommissioned_media"]


def _write_plan(tmp_path, resource_changes):
    path = tmp_path / "plan.json"
    path.write_text(json.dumps({"format_version": "1.2", "resource_changes": resource_changes}))
    return str(path)


def _rc(address, actions, tags):
    return {"address": address, "type": "aws_s3_bucket", "change": {"actions": actions, "after": {"tags": tags}}}


# 1. Happy path against the shared fixture

def test_fixture_flags_exactly_the_untagged_resources(capsys):
    code = check_plan(FIXTURE)
    out = capsys.readouterr().out

    assert code != 0
    flagged_lines = sorted(line.strip()[2:] for line in out.splitlines() if line.strip().startswith("- "))
    assert flagged_lines == sorted(FLAGGED)


def test_fixture_passes_resources_that_carry_landlord_account_id(capsys):
    check_plan(FIXTURE)
    out = capsys.readouterr().out

    for address in PASSING:
        assert address not in out


def test_tenant_id_tag_is_not_a_substitute_for_landlord_account_id(capsys):
    """listing_media carries tenant_id only, which is the 'ID on hand' trap from the README."""
    check_plan(FIXTURE)
    assert "aws_s3_bucket.listing_media" in capsys.readouterr().out


def test_fixture_noop_and_delete_entries_are_ignored_without_crashing(capsys):
    check_plan(FIXTURE)
    out = capsys.readouterr().out

    for address in SKIPPED:
        assert address not in out
    # 6 entries in the fixture; only the 4 create/update ones are counted. If no-op or delete
    # were checked, this would read "of 5" / "of 6" (and archive_media would be flagged).
    assert "2 of 4 resource(s)" in out


# 2. Idempotency

def test_running_twice_gives_identical_output_and_exit_code(capsys):
    first_code = check_plan(FIXTURE)
    first_out = capsys.readouterr().out
    second_code = check_plan(FIXTURE)
    second_out = capsys.readouterr().out

    assert first_code == second_code != 0
    assert first_out == second_out
    for address in FLAGGED:
        assert first_out.count(address) == 1


def test_duplicate_address_in_one_plan_is_reported_once(tmp_path, capsys):
    plan = _write_plan(tmp_path, [
        _rc("aws_s3_bucket.dupe", ["create"], {}),
        _rc("aws_s3_bucket.dupe", ["create"], {}),
    ])

    assert check_plan(plan) == 1
    out = capsys.readouterr().out
    assert out.count("aws_s3_bucket.dupe") == 1
    assert "1 of 1" in out


def test_output_is_independent_of_input_order(tmp_path, capsys):
    a = _rc("aws_s3_bucket.a", ["create"], {})
    b = _rc("aws_s3_bucket.b", ["update"], {"tenant_id": "ten-001"})

    check_plan(_write_plan(tmp_path, [a, b]))
    forward = capsys.readouterr().out
    check_plan(_write_plan(tmp_path, [b, a]))
    reverse = capsys.readouterr().out

    assert forward == reverse


# Edge cases

def test_all_tagged_plan_passes(tmp_path, capsys):
    plan = _write_plan(tmp_path, [_rc("aws_s3_bucket.ok", ["create"], {"landlord_account_id": "la-001"})])

    assert check_plan(plan) == 0
    assert "PASS" in capsys.readouterr().out


def test_replace_action_is_checked(tmp_path):
    plan = _write_plan(tmp_path, [_rc("aws_s3_bucket.replaced", ["delete", "create"], {})])

    assert check_plan(plan) == 1


def test_blank_or_null_tag_value_counts_as_missing(tmp_path):
    plan = _write_plan(tmp_path, [
        _rc("aws_s3_bucket.blank", ["create"], {"landlord_account_id": "  "}),
        _rc("aws_s3_bucket.nulltags", ["create"], None),
    ])

    assert check_plan(plan) == 1


def test_tag_inherited_via_default_tags_in_tags_all_passes(tmp_path):
    rc = {"address": "aws_s3_bucket.defaulted", "type": "aws_s3_bucket",
          "change": {"actions": ["create"], "after": {"tags": {}, "tags_all": {"landlord_account_id": "la-003"}}}}

    assert check_plan(_write_plan(tmp_path, [rc])) == 0


def test_unreadable_plan_fails_closed(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")

    assert check_plan(str(bad)) not in (0, None)
    assert check_plan(str(tmp_path / "missing.json")) not in (0, None)

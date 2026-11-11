"""
Write tests here proving:
  1. A PropertyManager scoped to la-001 (pm-001) is DENIED access to la-002's tenant's
     screening report (rep-002).
  2. The same PropertyManager (pm-001) IS allowed access to their own account's screening
     report (rep-001).

Use the `property_managers`, `properties`, `tenants`, and `screening_reports` fixtures from
conftest.py — don't re-invent the seed data here.
"""
import pytest

from app.access_control import can_access_screening_report
from app.models import Property, Tenant


def _by_id(records, record_id):
    return next(r for r in records if r.id == record_id)


def test_pm_001_denied_cross_account_report(property_managers, properties, tenants, screening_reports):
    pm_001 = _by_id(property_managers, "pm-001")
    rep_002 = _by_id(screening_reports, "rep-002")  # ten-002 -> prop-002 -> la-002

    assert can_access_screening_report(pm_001, rep_002, properties=properties, tenants=tenants) is False


def test_pm_001_allowed_own_account_report(property_managers, properties, tenants, screening_reports):
    pm_001 = _by_id(property_managers, "pm-001")
    rep_001 = _by_id(screening_reports, "rep-001")  # ten-001 -> prop-001 -> la-001

    assert can_access_screening_report(pm_001, rep_001, properties=properties, tenants=tenants) is True


@pytest.mark.parametrize(
    "pm_id, rep_id, expected",
    [
        ("pm-001", "rep-001", True),
        ("pm-001", "rep-002", False),
        ("pm-002", "rep-002", True),
        ("pm-002", "rep-001", False),
    ],
)
def test_access_matrix_is_symmetric(pm_id, rep_id, expected, property_managers, properties, tenants, screening_reports):
    pm = _by_id(property_managers, pm_id)
    rep = _by_id(screening_reports, rep_id)

    assert can_access_screening_report(pm, rep, properties=properties, tenants=tenants) is expected


def test_fails_closed_when_tenant_missing(property_managers, properties, tenants, screening_reports):
    pm_001 = _by_id(property_managers, "pm-001")
    rep_001 = _by_id(screening_reports, "rep-001")
    tenants_without_ten_001 = [t for t in tenants if t.id != "ten-001"]

    assert can_access_screening_report(pm_001, rep_001, properties=properties, tenants=tenants_without_ten_001) is False


def test_fails_closed_when_property_missing(property_managers, properties, tenants, screening_reports):
    pm_001 = _by_id(property_managers, "pm-001")
    rep_001 = _by_id(screening_reports, "rep-001")
    properties_without_prop_001 = [p for p in properties if p.id != "prop-001"]

    assert can_access_screening_report(pm_001, rep_001, properties=properties_without_prop_001, tenants=tenants) is False


def test_fails_closed_when_tenant_id_is_ambiguous(property_managers, properties, tenants, screening_reports):
    """A duplicate tenant id pointing at another account must not grant access by list order."""
    pm_002 = _by_id(property_managers, "pm-002")
    rep_001 = _by_id(screening_reports, "rep-001")
    tenants_with_dupe = [Tenant(id="ten-001", name="Impostor", property_id="prop-002"), *tenants]

    assert can_access_screening_report(pm_002, rep_001, properties=properties, tenants=tenants_with_dupe) is False


def test_fails_closed_when_property_has_no_landlord_account(property_managers, tenants, screening_reports):
    pm_001 = _by_id(property_managers, "pm-001")
    rep_001 = _by_id(screening_reports, "rep-001")
    orphan_props = [Property(id="prop-001", landlord_account_id="", address="12 Maple St")]

    assert can_access_screening_report(pm_001, rep_001, properties=orphan_props, tenants=tenants) is False

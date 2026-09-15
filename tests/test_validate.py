"""The canonical contract, and the architecture rule it enforces."""

import pandas as pd
import pytest

from bootcamp.validate import SchemaError, validate_all, validate_table


def test_valid_hours_passes_and_is_typed(hours_df):
    out = validate_table("hours_entry", hours_df)
    assert list(out.columns) == [
        "entry_id", "date", "employee_ref", "crew_ref", "job_ref",
        "ops_service_line", "ops_code", "hours", "source_system",
    ]
    assert pd.api.types.is_datetime64_any_dtype(out["date"])
    assert out["hours"].sum() == pytest.approx(16.75)


def test_optional_field_may_be_absent_entirely(hours_df):
    out = validate_table("hours_entry", hours_df.drop(columns=["crew_ref"]))
    assert out["crew_ref"].isna().all()


def test_missing_required_field_is_rejected(hours_df):
    with pytest.raises(SchemaError, match="required field.*ops_code"):
        validate_table("hours_entry", hours_df.drop(columns=["ops_code"]))


def test_null_in_required_field_is_rejected(hours_df):
    hours_df.loc[1, "ops_service_line"] = None
    with pytest.raises(SchemaError, match="null in 1 row"):
        validate_table("hours_entry", hours_df)


def test_unparseable_number_is_rejected(hours_df):
    # a CSV with a stray text value reads back as an object column, which is
    # the shape the validator has to reject
    hours_df["hours"] = hours_df["hours"].astype(object)
    hours_df.loc[0, "hours"] = "seven and a half"
    with pytest.raises(SchemaError, match="not coercible to decimal"):
        validate_table("hours_entry", hours_df)


def test_enum_is_enforced(roster_df):
    roster_df.loc[0, "classification"] = "supervisor"
    with pytest.raises(SchemaError, match="outside the allowed set"):
        validate_table("roster", roster_df)


def test_all_problems_reported_together(hours_df):
    broken = hours_df.drop(columns=["ops_code", "entry_id"])
    with pytest.raises(SchemaError) as excinfo:
        validate_table("hours_entry", broken)
    assert "ops_code" in str(excinfo.value) and "entry_id" in str(excinfo.value)


def test_validate_all_reports_every_table(hours_df, roster_df):
    with pytest.raises(SchemaError) as excinfo:
        validate_all(
            {
                "hours_entry": hours_df.drop(columns=["hours"]),
                "roster": roster_df.drop(columns=["name"]),
            }
        )
    assert "hours_entry" in str(excinfo.value) and "roster" in str(excinfo.value)


class TestAdaptersTranslateFormatNotMeaning:
    """data-architecture.md §3 — the rule, enforced rather than documented."""

    def test_adapter_may_not_decide_billable(self, hours_df):
        hours_df["billable"] = [True, False, True]
        with pytest.raises(SchemaError) as excinfo:
            validate_table("hours_entry", hours_df)
        message = str(excinfo.value)
        assert "must not be emitted by an adapter" in message
        assert "client's own convention" in message
        assert "layer 4" in message

    def test_adapter_may_not_resolve_financial_service_line(self, hours_df):
        hours_df["service_line"] = ["Maintenance", "Maintenance", "Install"]
        with pytest.raises(SchemaError, match="service_line_map"):
            validate_table("hours_entry", hours_df)

    def test_adapter_may_not_map_accounts_to_categories(self):
        gl = pd.DataFrame(
            {
                "account_raw": ["Fuel"],
                "section_hint": ["OH"],
                "month": ["2025-05-01"],
                "amount": [1200.0],
                "source_system": ["qbo"],
                "standard_category": ["Vehicle + Equipment [OH]"],
            }
        )
        with pytest.raises(SchemaError, match="registry"):
            validate_table("gl_monthly", gl)

    def test_unknown_column_is_rejected_with_a_pointer_to_config(self, hours_df):
        hours_df["crew_lead_bonus_eligible"] = [True, True, False]
        with pytest.raises(SchemaError, match="client config"):
            validate_table("hours_entry", hours_df)

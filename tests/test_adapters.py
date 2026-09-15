"""Adapter registry, the generic CSV path, and the two stubs."""

from pathlib import Path

import pandas as pd
import pytest

from bootcamp import adapters
from bootcamp.validate import validate_table

DEMO = Path(__file__).resolve().parents[1] / "clients/_demo/raw/ops/hours.csv"


def test_every_registered_adapter_declares_its_contract():
    registry = adapters.registered()
    assert registry, "no adapters registered"
    for key, adapter in registry.items():
        assert adapter.source_system == key
        assert adapter.kind in {adapters.OPS, adapters.ACCOUNTING}
        assert adapter.produces
        assert adapter.description


def test_extract_signature_takes_no_client(monkeypatch):
    """An adapter that needs to know which client it is running for is five
    adapters wearing a trench coat. The signature is the guard."""
    import inspect

    for adapter in adapters.registered().values():
        params = list(inspect.signature(adapter.extract).parameters)
        assert params == ["paths"], f"{adapter.source_system}.extract takes {params}"


def test_unknown_adapter_names_the_registered_ones():
    with pytest.raises(KeyError, match="Registered:"):
        adapters.get("synkedup")


class TestGenericCsv:
    def test_demo_export_survives_the_round_trip(self):
        tables = adapters.get("generic_csv").extract([DEMO])
        assert set(tables) == {"hours_entry"}
        out = validate_table("hours_entry", tables["hours_entry"])
        assert len(out) > 500
        assert out["source_system"].eq("generic_csv").all()
        assert out["hours"].gt(0).all()

    def test_no_input_files_is_an_error(self):
        with pytest.raises(ValueError, match="no input files"):
            adapters.get("generic_csv").extract([])


class TestLmnStub:
    def test_unfilled_column_map_names_every_missing_field(self, tmp_path):
        sample = tmp_path / "lmn.csv"
        pd.DataFrame({"Date": ["2025-05-01"], "Hours": [8.0]}).to_csv(sample, index=False)
        with pytest.raises(adapters.NotYetMapped) as excinfo:
            adapters.get("lmn").extract([sample])
        assert "ops_code" in excinfo.value.unmapped
        assert "COLUMN_MAP" in str(excinfo.value)

    def test_filling_in_the_column_map_is_the_only_change_needed(self, tmp_path, monkeypatch):
        """Proves the stub is wired, not just documented: supply a map and a
        matching file and the adapter produces a valid canonical table."""
        from bootcamp.adapters import ops_lmn

        monkeypatch.setattr(
            ops_lmn,
            "COLUMN_MAP",
            {
                "entry_id": "TimeEntryID",
                "date": "WorkDate",
                "employee_ref": "",       # crew-based export: deliberately absent
                "crew_ref": "CrewName",
                "job_ref": "JobNumber",
                "ops_service_line": "Division",
                "ops_code": "ActivityCode",
                "hours": "TotalHours",
            },
        )
        sample = tmp_path / "lmn.csv"
        pd.DataFrame(
            {
                "TimeEntryID": ["T1", "T2"],
                "WorkDate": ["2025-05-01", "2025-05-01"],
                "CrewName": ["CREW-01", "CREW-01"],
                "JobNumber": ["J1", "J2"],
                "Division": ["Maintenance", "Maintenance"],
                "ActivityCode": ["MOW", "DRIVE"],
                "TotalHours": [7.5, 1.0],
            }
        ).to_csv(sample, index=False)

        tables = adapters.get("lmn").extract([sample])
        out = validate_table("hours_entry", tables["hours_entry"])
        assert len(out) == 2
        assert out["employee_ref"].isna().all()
        assert out["source_system"].eq("lmn").all()
        assert set(out["ops_code"]) == {"MOW", "DRIVE"}

    def test_export_missing_a_mapped_column_says_what_it_found(self, tmp_path, monkeypatch):
        from bootcamp.adapters import ops_lmn

        monkeypatch.setattr(
            ops_lmn, "COLUMN_MAP",
            {k: v for k, v in [
                ("entry_id", "TimeEntryID"), ("date", "WorkDate"),
                ("employee_ref", ""), ("crew_ref", "CrewName"), ("job_ref", ""),
                ("ops_service_line", "Division"), ("ops_code", "ActivityCode"),
                ("hours", "TotalHours"),
            ]},
        )
        sample = tmp_path / "lmn.csv"
        pd.DataFrame({"TimeEntryID": ["T1"], "WorkDate": ["2025-05-01"]}).to_csv(sample, index=False)
        with pytest.raises(ValueError, match="missing expected column"):
            adapters.get("lmn").extract([sample])


class TestQboStub:
    def test_parse_is_unfinished_and_says_so(self, tmp_path):
        sample = tmp_path / "pl.csv"
        sample.write_text("Acme Landscaping\nProfit and Loss\n\n,Jan 2025\nIncome,\n")
        with pytest.raises(NotImplementedError, match="_parse_pl"):
            adapters.get("qbo").extract([sample])

    def test_declares_both_gl_tables(self):
        assert set(adapters.get("qbo").produces) == {"gl_monthly", "gl_period_by_class"}

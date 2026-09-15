import pandas as pd
import pytest


@pytest.fixture
def hours_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "entry_id": ["E1", "E2", "E3"],
            "date": ["2025-05-01", "2025-05-01", "2025-05-02"],
            "employee_ref": [None, None, None],
            "crew_ref": ["CREW-01", "CREW-01", "CREW-02"],
            "job_ref": ["J1", None, "J2"],
            "ops_service_line": ["Maintenance", "Maintenance", "Install"],
            "ops_code": ["MOW", "DRIVE", "PLANT"],
            "hours": [7.5, 1.25, 8.0],
            "source_system": ["generic_csv"] * 3,
        }
    )


@pytest.fixture
def roster_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "employee_ref": ["1", "2"],
            "name": ["A. Foreman", "B. Controller"],
            "service_line_raw": ["Maintenance", "Overhead"],
            "classification": ["field", "overhead"],
            "pay_type": ["hourly", "salary"],
            "pay_rate": [24.0, None],
            "annual_salary": [None, 78000.0],
            "source_system": ["qbo", "qbo"],
        }
    )

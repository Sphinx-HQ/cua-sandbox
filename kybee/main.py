import pydantic
from pathlib import Path


class NoteAndEmail(pydantic.BaseModel):
    note: str
    email: str


def process_kyb(
    folder_path: Path,
    business_name: str,
    date_submitted: str,
    loan_amount_usd: float | int,
    loan_amount_brl: float | int,
) -> NoteAndEmail:
    return NoteAndEmail(
        note="Our note here",
        email="Our email here",
    )

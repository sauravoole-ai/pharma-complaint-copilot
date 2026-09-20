import pytest

from app.domain.schemas import ComplaintFields, DraftStatus
from app.services.corrections import (
    InvalidCorrection,
    apply_correction,
    reconcile_corrected_summary,
)
from tests.fakes import FakeLLMAdapter


@pytest.fixture
def complete_fields() -> ComplaintFields:
    return ComplaintFields(
        complaint_source="Email",
        customer_name="Northstar Pharmacy",
        product_name="Amoxicillin",
        batch_lot_number="AMX240602",
        affected_quantity="40 capsules",
        complaint_category="Product quality",
        complaint_description="Capsules appeared discolored.",
    )


def test_batch_and_quantity_correction_changes_only_two_fields(complete_fields):
    llm = FakeLLMAdapter(
        correction={
            "batch_lot_number": "BMX240602",
            "affected_quantity": "48 capsules",
        }
    )

    updated = apply_correction(
        complete_fields,
        "The batch is BMX240602 and quantity is 48 capsules",
        llm,
    )

    assert updated.fields.batch_lot_number == "BMX240602"
    assert updated.fields.affected_quantity == "48 capsules"
    assert updated.fields.customer_name == complete_fields.customer_name
    assert updated.changed_fields == ["batch_lot_number", "affected_quantity"]
    assert updated.status == DraftStatus.READY_TO_COMMIT


def test_reconcile_corrected_summary_replaces_a_stale_changed_value(complete_fields):
    updated_fields = complete_fields.model_copy(update={"affected_quantity": "25 capsules"})

    summary = reconcile_corrected_summary(
        "Northstar Pharmacy reported that 40 capsules appeared darker than usual.",
        complete_fields,
        updated_fields,
        ["affected_quantity"],
    )

    assert "25 capsules" in summary
    assert "40 capsules" not in summary


@pytest.mark.parametrize(
    "patch",
    [
        {},
        {"owner": "someone"},
        {"customer_name": "x" * 501},
    ],
)
def test_invalid_patch_is_rejected(complete_fields, patch):
    with pytest.raises(InvalidCorrection):
        apply_correction(complete_fields, "change it", FakeLLMAdapter(correction=patch))

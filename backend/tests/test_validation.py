from app.domain.schemas import ComplaintFields, DraftStatus
from app.services.validation import validate_and_classify


def complete_fields() -> ComplaintFields:
    return ComplaintFields(
        complaint_source="Pharmacy",
        customer_name="Apollo Pharmacy",
        product_type="FDF",
        product_name="Amoxicillin Capsules",
        product_strength="500 mg",
        batch_lot_number="AMX240602",
        affected_quantity="12 capsules",
        manufacturing_date="March 2026",
        expiry_date="February 2028",
        originating_site_block="Manufacturing",
        impacted_non_product_materials="Primary Packaging (Bottle)",
        complaint_category="Product Defect - Discoloration",
        complaint_description="Twelve discolored capsules were found in a sealed bottle.",
        customer_requested_action="Investigation and replacement",
    )


def test_missing_batch_requires_review() -> None:
    fields = complete_fields().model_copy(update={"batch_lot_number": None})

    completeness, status = validate_and_classify(fields)

    assert completeness.missing_fields == ["batch_lot_number"]
    assert completeness.is_complete is False
    assert status == DraftStatus.NEEDS_REVIEW


def test_whitespace_customer_name_is_missing() -> None:
    fields = complete_fields().model_copy(update={"customer_name": "   "})

    completeness, status = validate_and_classify(fields)

    assert completeness.missing_fields == ["customer_name"]
    assert status == DraftStatus.NEEDS_REVIEW


def test_complete_fields_are_ready_to_commit() -> None:
    completeness, status = validate_and_classify(complete_fields())

    assert completeness.is_complete is True
    assert completeness.missing_fields == []
    assert status == DraftStatus.READY_TO_COMMIT

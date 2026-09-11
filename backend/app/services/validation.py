from app.domain.schemas import ComplaintFields, CompletenessResult, DraftStatus

REQUIRED_FIELDS = (
    "complaint_source",
    "customer_name",
    "product_name",
    "batch_lot_number",
    "complaint_category",
    "complaint_description",
)


def _is_missing(value: str | None) -> bool:
    return value is None or not value.strip()


def validate_and_classify(
    fields: ComplaintFields,
) -> tuple[CompletenessResult, DraftStatus]:
    missing = [name for name in REQUIRED_FIELDS if _is_missing(getattr(fields, name))]
    completeness = CompletenessResult(
        is_complete=not missing,
        missing_fields=missing,
    )
    status = DraftStatus.READY_TO_COMMIT if completeness.is_complete else DraftStatus.NEEDS_REVIEW
    return completeness, status

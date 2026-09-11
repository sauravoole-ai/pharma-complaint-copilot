from app.domain.schemas import ComplaintFields, RiskSuggestion, Severity


class FakeLLMAdapter:
    def __init__(
        self,
        *,
        omit_batch: bool = False,
        correction: dict[str, str | None] | None = None,
    ):
        self.omit_batch = omit_batch
        self.correction = {"batch_lot_number": "BMX240602"} if correction is None else correction
        self.calls: list[str] = []

    def extract(self, source_text: str) -> ComplaintFields:
        self.calls.append("extract")
        return ComplaintFields(
            complaint_source="Email",
            customer_name="Northstar Pharmacy",
            product_type="Capsule",
            product_name="Amoxicillin",
            product_strength="500 mg",
            batch_lot_number=None if self.omit_batch else "AMX240602",
            affected_quantity="48 capsules",
            complaint_category="Product quality",
            complaint_description=source_text,
            customer_requested_action="Replacement and investigation",
        )

    def suggest_risk(self, fields: ComplaintFields) -> RiskSuggestion:
        self.calls.append("suggest_risk")
        return RiskSuggestion(
            severity=Severity.MAJOR,
            next_action="Quarantine the batch and begin a quality investigation.",
            rationale="Discoloration may indicate a product-quality defect.",
        )

    def summarize(self, fields: ComplaintFields) -> str:
        self.calls.append("summarize")
        return "Northstar Pharmacy reported discoloration in Amoxicillin 500 mg capsules."

    def correction_patch(self, fields: ComplaintFields, instruction: str) -> dict[str, str | None]:
        self.calls.append("correction_patch")
        return self.correction

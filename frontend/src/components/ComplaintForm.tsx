import type { ComplaintFields } from "../types/complaint";

type FieldName = keyof ComplaintFields;

const fieldGroups: { title: string; fields: { name: FieldName; label: string; wide?: boolean }[] }[] = [
  {
    title: "Customer & source",
    fields: [
      { name: "complaint_source", label: "Complaint source" },
      { name: "customer_name", label: "Customer name" },
    ],
  },
  {
    title: "Product details",
    fields: [
      { name: "product_type", label: "Product type" },
      { name: "product_name", label: "Product name" },
      { name: "product_strength", label: "Strength" },
      { name: "batch_lot_number", label: "Batch / lot number" },
      { name: "affected_quantity", label: "Affected quantity" },
      { name: "manufacturing_date", label: "Manufacturing date" },
      { name: "expiry_date", label: "Expiry date" },
      { name: "originating_site_block", label: "Originating site / block" },
    ],
  },
  {
    title: "Complaint details",
    fields: [
      {
        name: "impacted_non_product_materials",
        label: "Impacted non-product materials",
      },
      { name: "complaint_category", label: "Complaint category" },
      { name: "complaint_description", label: "Complaint description", wide: true },
      { name: "customer_requested_action", label: "Customer requested action", wide: true },
    ],
  },
];

export function ComplaintForm({
  fields,
  missingFields,
  disabled,
  onChange,
}: {
  fields: ComplaintFields;
  missingFields: string[];
  disabled: boolean;
  onChange: (field: FieldName, value: string) => void;
}) {
  return (
    <div className="complaint-form">
      {fieldGroups.map((group) => (
        <fieldset key={group.title} disabled={disabled}>
          <legend>{group.title}</legend>
          <div className="field-grid">
            {group.fields.map((field) => {
              const isLong = field.wide;
              const isMissing = missingFields.includes(field.name);
              const id = `field-${field.name}`;
              return (
                <label className={isLong ? "field field--wide" : "field"} key={field.name}>
                  <span>
                    {field.label}
                    {isMissing && <em>Required</em>}
                  </span>
                  {isLong ? (
                    <textarea
                      id={id}
                      rows={3}
                      value={fields[field.name] ?? ""}
                      aria-invalid={isMissing}
                      onChange={(event) => onChange(field.name, event.target.value)}
                    />
                  ) : (
                    <input
                      id={id}
                      value={fields[field.name] ?? ""}
                      aria-invalid={isMissing}
                      onChange={(event) => onChange(field.name, event.target.value)}
                    />
                  )}
                </label>
              );
            })}
          </div>
        </fieldset>
      ))}
    </div>
  );
}

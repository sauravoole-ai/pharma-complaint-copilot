from pathlib import Path

LINES = [
    "Synthetic pharmaceutical customer complaint",
    "",
    "Source: Customer quality portal",
    "Customer: Meridian Hospital Pharmacy",
    "Product: Ceftriaxone for Injection 1 g",
    "Batch / lot: CFX260811",
    "Affected quantity: 3 vials",
    "Category: Foreign matter / visible particulate",
    "",
    "The customer reported a dark visible particle in three unopened vials.",
    "The vials were segregated before use. No patient exposure was reported.",
    "The customer requested urgent investigation and replacement stock.",
    "",
    "This is fictional test data created for a software demonstration.",
]


def pdf_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list[str]) -> bytes:
    text_commands = ["BT", "/F1 11 Tf", "48 760 Td", "15 TL"]
    for index, line in enumerate(lines):
        if index:
            text_commands.append("T*")
        text_commands.append(f"({pdf_string(line)}) Tj")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(payload)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "samples" / "foreign-matter-complaint.pdf"
    target.write_bytes(build_pdf(LINES))
    print(f"Wrote {target}")

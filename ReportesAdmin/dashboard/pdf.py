from __future__ import annotations

from io import BytesIO
from typing import Iterable, Mapping

from django.utils import timezone


def _escape(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _chunk_lines(lines: list[str], per_page: int = 40) -> list[list[str]]:
    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= per_page:
            pages.append(current)
            current = []
    if current:
        pages.append(current)
    return pages or [[]]


def generate_report_pdf(*, title: str, filters: Mapping[str, object], rows: Iterable, summary: Mapping[str, object]) -> bytes:
    lines: list[str] = [title, '']
    for key, value in filters.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value}")
    if filters:
        lines.append('')
    header = f"{'Producto':<40} {'Cant.':>6} {'Precio':>10} {'Subtotal':>12} Estado"
    lines.append(header)
    lines.append('-' * len(header))
    for item in rows:
        created = None
        if item.sale and item.sale.created_at:
            created_at = item.sale.created_at
            if timezone.is_naive(created_at):
                created_at = timezone.make_aware(created_at, timezone.get_current_timezone())
            created = timezone.localtime(created_at)
        lines.append(
            f"{item.product_name[:38]:<40} {item.quantity:>6} {float(item.unit_price):>10.2f} {float(item.subtotal):>12.2f} {item.get_status_display()}"
        )
        if item.category_name:
            lines.append(f"  Categoría: {item.category_name}")
        if created:
            lines.append(f"  Fecha: {created.strftime('%d/%m/%Y %H:%M')}")
    lines.append('')
    lines.append(f"Total de unidades: {summary.get('cantidad', 0)}")
    lines.append(f"Total vendido: ${float(summary.get('total', 0)):.2f}")

    pages = _chunk_lines(lines)

    objects: list[bytes | None] = [None]  
    catalog_id = len(objects)
    objects.append(None)
    pages_id = len(objects)
    objects.append(None)
    font_id = len(objects)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_ids: list[int] = []
    content_ids: list[int] = []

    for page_lines in pages:
        y = 780
        content_stream_lines = []
        for line in page_lines:
            content_stream_lines.append(f"BT /F1 12 Tf 50 {y} Td ({_escape(line)}) Tj ET")
            y -= 16
        content_bytes = "\n".join(content_stream_lines).encode('latin-1', 'ignore')
        content_obj = f"<< /Length {len(content_bytes)} >>\nstream\n".encode() + content_bytes + b"\nendstream"
        content_id = len(objects)
        objects.append(content_obj)
        content_ids.append(content_id)

        page_obj = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
        ).encode()
        page_id = len(objects)
        objects.append(page_obj)
        page_ids.append(page_id)

    kids = ' '.join(f"{pid} 0 R" for pid in page_ids) or ""
    objects[pages_id] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    objects[catalog_id] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()

    buffer = BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets: list[int] = []
    for idx, obj in enumerate(objects[1:], start=1):
        if obj is None:
            continue
        offsets.append(buffer.tell())
        buffer.write(f"{idx} 0 obj\n".encode())
        buffer.write(obj)
        buffer.write(b"\nendobj\n")

    xref_pos = buffer.tell()
    buffer.write(f"xref\n0 {len(objects)}\n".encode())
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buffer.write(f"{offset:010d} 00000 n \n".encode())
    buffer.write(f"trailer\n<< /Size {len(objects)} /Root {catalog_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode())
    return buffer.getvalue()
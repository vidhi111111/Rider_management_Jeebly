import io
import csv
from typing import List, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def generate_csv_data(headers: List[str], rows: List[List[Any]]) -> str:
    """Generate RFC-4180 CSV string with UTF-8 BOM for universal Excel compatibility."""
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([str(cell) if cell is not None else "" for cell in row])
    return output.getvalue()


def generate_excel_data(sheet_title: str, headers: List[str], rows: List[List[Any]]) -> bytes:
    """Generate styled Microsoft Excel (.xlsx) workbook bytes matching Jeebly branding."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title[:31]

    # Jeebly Brand Header Styling: Jeebly Blue (#163758)
    header_fill = PatternFill(start_color="163758", end_color="163758", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Arial", size=10, color="183B5B")
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    for row_idx, row_data in enumerate(rows, start=2):
        ws.append([cell if cell is not None else "" for cell in row_data])
        ws.row_dimensions[row_idx].height = 22
        is_even = (row_idx % 2 == 0)
        for col_idx in range(1, len(row_data) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if is_even:
                cell.fill = zebra_fill
            cell.alignment = left_align

    # Auto-fit column widths with padding
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

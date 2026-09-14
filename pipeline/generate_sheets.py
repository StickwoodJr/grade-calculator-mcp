#!/usr/bin/env python3
"""
Executive-Grade Grade Calculator Spreadsheet Generator.

Generates 'grade_calculator.xlsx' using openpyxl with Seneca Polytechnic
Computer Systems Technology (CTY) Semester 3 curriculum.

Design System:
  - Theme: Modern Executive Academic (Deep Royal Navy, Ice Blue Inputs, Crisp Cards)
  - Typography: Segoe UI, clean scale, proper hierarchy
  - UX: Distinct ice-blue input cells, symmetrical 2-column KPI cards,
        jump hyperlinks between all sheets, accounting double-bottom totals,
        zero-error safe formulas (no #VALUE! on blank states).

Tabs:
  1. Dashboard & GPA (Executive overview, real-time GPA, technical core isolation)
  2-8. Course Sheets (CSN305, DAT330, MST300, PSY262, SEC320, OPS345, WTP100)
  9. What-If Simulator (Target grade solver & exam score requirements)
  10. Timeline & Milestones (Chronological semester deliverable tracker)
"""

import os
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==============================================================================
# Design System Constants
# ==============================================================================
FONT_NAME = "Segoe UI"

# Colors
C_NAVY_DARK = "0F172A"       # Slate 900
C_NAVY_HEADER = "1E3A8A"     # Deep Royal Navy (Table headers)
C_NAVY_SUB = "1E293B"        # Slate 800
C_CARD_BG = "F8FAFC"         # Slate 50 (Card background)
C_CARD_BORDER = "CBD5E1"     # Slate 300 (Card border)
C_CARD_LABEL = "475569"      # Slate 600 (Card uppercase label)
C_INPUT_FILL = "EFF6FF"      # Blue 50 (Editable input cell background)
C_INPUT_BORDER = "93C5FD"    # Blue 300 (Input cell border)
C_INPUT_TEXT = "1E40AF"      # Blue 800 (Input text bold)
C_ZEBRA = "F8FAFC"           # Slate 50 alternating rows
C_WHITE = "FFFFFF"
C_BORDER_LIGHT = "E2E8F0"    # Table border light slate
C_BORDER_MED = "94A3B8"

# Status colors
C_DONE_BG = "DCFCE7"         # Green 100
C_DONE_TXT = "166534"        # Green 800
C_PROG_BG = "FEF3C7"         # Amber 100
C_PROG_TXT = "92400E"        # Amber 800
C_TODO_BG = "F1F5F9"         # Slate 100
C_TODO_TXT = "475569"        # Slate 600
C_ALERT_BG = "FEE2E2"        # Red 100
C_ALERT_TXT = "991B1B"       # Red 800

# Fonts
F_TITLE = Font(name=FONT_NAME, size=15, bold=True, color=C_NAVY_DARK)
F_SUBTITLE = Font(name=FONT_NAME, size=9.5, italic=True, color="64748B")
F_CARD_LABEL = Font(name=FONT_NAME, size=8.5, bold=True, color=C_CARD_LABEL)
F_CARD_METRIC = Font(name=FONT_NAME, size=17, bold=True, color=C_NAVY_DARK)
F_CARD_SUB = Font(name=FONT_NAME, size=8, italic=True, color="64748B")
F_TH = Font(name=FONT_NAME, size=9.5, bold=True, color=C_WHITE)
F_DATA = Font(name=FONT_NAME, size=9.5, color=C_NAVY_DARK)
F_DATA_BOLD = Font(name=FONT_NAME, size=9.5, bold=True, color=C_NAVY_DARK)
F_INPUT = Font(name=FONT_NAME, size=9.5, bold=True, color=C_INPUT_TEXT)
F_TOTAL = Font(name=FONT_NAME, size=9.5, bold=True, color=C_NAVY_DARK)
F_LINK = Font(name=FONT_NAME, size=9.5, bold=True, color="2563EB", underline="single")

# Fills
FILL_NAVY_HEADER = PatternFill(fill_type="solid", start_color=C_NAVY_HEADER, end_color=C_NAVY_HEADER)
FILL_CARD = PatternFill(fill_type="solid", start_color=C_CARD_BG, end_color=C_CARD_BG)
FILL_INPUT = PatternFill(fill_type="solid", start_color=C_INPUT_FILL, end_color=C_INPUT_FILL)
FILL_ZEBRA = PatternFill(fill_type="solid", start_color=C_ZEBRA, end_color=C_ZEBRA)
FILL_WHITE = PatternFill(fill_type="solid", start_color=C_WHITE, end_color=C_WHITE)
FILL_NOTICE = PatternFill(fill_type="solid", start_color="EFF6FF", end_color="EFF6FF")
FILL_HURDLE_BANNER = PatternFill(fill_type="solid", start_color="FEF3C7", end_color="FEF3C7")
FILL_DONE = PatternFill(fill_type="solid", start_color=C_DONE_BG, end_color=C_DONE_BG)
FILL_PROG = PatternFill(fill_type="solid", start_color=C_PROG_BG, end_color=C_PROG_BG)
FILL_TODO = PatternFill(fill_type="solid", start_color=C_TODO_BG, end_color=C_TODO_BG)
FILL_TOTAL = PatternFill(fill_type="solid", start_color="F1F5F9", end_color="F1F5F9")

# Borders
B_THIN = Side(style="thin", color=C_BORDER_LIGHT)
B_MED = Side(style="medium", color=C_BORDER_MED)
B_DOUBLE = Side(style="double", color=C_NAVY_DARK)
B_BLUE = Side(style="thin", color=C_INPUT_BORDER)
B_CARD_SIDE = Side(style="thin", color=C_CARD_BORDER)

BORDER_CELL = Border(left=B_THIN, right=B_THIN, top=B_THIN, bottom=B_THIN)
BORDER_INPUT = Border(left=B_BLUE, right=B_BLUE, top=B_BLUE, bottom=B_BLUE)
BORDER_TOTAL = Border(top=B_THIN, bottom=B_DOUBLE, left=B_THIN, right=B_THIN)
BORDER_CARD = Border(left=B_CARD_SIDE, right=B_CARD_SIDE, top=B_CARD_SIDE, bottom=B_CARD_SIDE)


def style_range(ws, cell_range, font=None, fill=None, border=None, alignment=None, number_format=None):
    """Applies styles to all cells in a range, ensuring merged areas format seamlessly."""
    for row in ws[cell_range]:
        for cell in row:
            if font: cell.font = font
            if fill: cell.fill = fill
            if border: cell.border = border
            if alignment: cell.alignment = alignment
            if number_format: cell.number_format = number_format


def auto_fit_columns(ws, min_width=12, max_width=45):
    """Calculates clean column widths with breathing room."""
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            # Skip merged title and banner rows when calculating column width
            if cell.row in [1, 2, 3, 4, 8, 9]:
                continue
            val = str(cell.value or "")
            if val.startswith("="):
                val = "100.0%"  # typical formula width estimate
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, min_width), max_width)


def render_kpi_card(ws, col_start_idx, row_start, label, formula_or_val, subtitle, num_format=None):
    """
    Renders a unified, professional 2-column x 3-row KPI Card.
    Example: Cols A-B, Rows 5-7.
    """
    c1 = get_column_letter(col_start_idx)
    c2 = get_column_letter(col_start_idx + 1)
    
    r_lbl = row_start
    r_val = row_start + 1
    r_sub = row_start + 2

    # Merge rows across the 2 columns
    ws.merge_cells(f"{c1}{r_lbl}:{c2}{r_lbl}")
    ws.merge_cells(f"{c1}{r_val}:{c2}{r_val}")
    ws.merge_cells(f"{c1}{r_sub}:{c2}{r_sub}")

    # Set content
    ws[f"{c1}{r_lbl}"] = label
    ws[f"{c1}{r_val}"] = formula_or_val
    ws[f"{c1}{r_sub}"] = subtitle

    # Style label
    style_range(ws, f"{c1}{r_lbl}:{c2}{r_lbl}",
                font=F_CARD_LABEL, fill=FILL_CARD, border=BORDER_CARD,
                alignment=Alignment(horizontal="center", vertical="center"))

    # Style metric
    style_range(ws, f"{c1}{r_val}:{c2}{r_val}",
                font=F_CARD_METRIC, fill=FILL_CARD, border=BORDER_CARD,
                alignment=Alignment(horizontal="center", vertical="center"),
                number_format=num_format)

    # Style subtitle
    style_range(ws, f"{c1}{r_sub}:{c2}{r_sub}",
                font=F_CARD_SUB, fill=FILL_CARD, border=BORDER_CARD,
                alignment=Alignment(horizontal="center", vertical="center"))


def generate_workbook(data_dir="data/courses", output_file="grade_calculator.xlsx"):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove openpyxl default sheet

    # Load course definitions
    with open(os.path.join(data_dir, "courses_index.json"), "r") as f:
        index_data = json.load(f)

    courses = []
    for c_info in index_data["courses"]:
        file_path = os.path.join(data_dir, c_info["file"])
        with open(file_path, "r") as f:
            courses.append(json.load(f))

    # ==============================================================================
    # 1. Individual Course Tabs (CSN305 through WTP100)
    # ==============================================================================
    course_sheet_meta = {}

    for c in courses:
        code = c["course_code"]
        ws = wb.create_sheet(title=code)
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = "A11"  # Freezes header row 10 and top KPI cards

        # Row Heights for spacious layout
        ws.row_dimensions[1].height = 24
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[3].height = 20
        ws.row_dimensions[4].height = 8   # spacer
        ws.row_dimensions[5].height = 16  # card label
        ws.row_dimensions[6].height = 26  # card metric
        ws.row_dimensions[7].height = 16  # card sub
        ws.row_dimensions[8].height = 8   # spacer
        ws.row_dimensions[9].height = 20  # input guidance banner
        ws.row_dimensions[10].height = 26 # table header

        # Row 1: Course Title + Return Link
        ws.merge_cells("A1:H1")
        ws["A1"] = f"{code}: {c['course_name']}"
        ws["A1"].font = F_TITLE
        ws["A1"].alignment = Alignment(vertical="center")

        ws.merge_cells("I1:J1")
        ws["I1"] = '=HYPERLINK("#\'Dashboard & GPA\'!A1", "⬅ Back to Dashboard")'
        style_range(ws, "I1:J1", font=Font(name=FONT_NAME, size=9.5, bold=True, color=C_WHITE),
                    fill=FILL_NAVY_HEADER, border=BORDER_CELL,
                    alignment=Alignment(horizontal="center", vertical="center"))

        # Row 2: Metadata Subtitle
        tech_str = "Technical Computing Core" if c["is_technical"] else ("Co-op Prep" if c["grading_type"] == "sat_un" else "General Elective")
        ws.merge_cells("A2:J2")
        ws["A2"] = f"Credits: {c['credits']}  •  Classification: {tech_str}  •  Grade Scale: {c['grade_scale']}"
        ws["A2"].font = F_SUBTITLE
        ws["A2"].alignment = Alignment(vertical="center")

        # Row 3: Hurdle Warning Banner
        ws.merge_cells("A3:J3")
        criteria_str = "📌 PASSING REQUIREMENTS: " + "  •  ".join(c.get("passing_criteria", []))
        ws["A3"] = criteria_str
        style_range(ws, "A3:J3", font=Font(name=FONT_NAME, size=8.5, bold=True, color="92400E"),
                    fill=FILL_HURDLE_BANNER, border=BORDER_CELL,
                    alignment=Alignment(vertical="center", indent=1))

        # Row 9: Input Guidance Callout
        ws.merge_cells("A9:J9")
        ws["A9"] = "💡 ENTER MARKS: Enter your points earned in the light blue 'Earned Pts' column (Col E). Scores, weighted points, and GPA recalculate automatically."
        style_range(ws, "A9:J9", font=Font(name=FONT_NAME, size=8.5, italic=True, color=C_INPUT_TEXT),
                    fill=FILL_NOTICE, border=BORDER_INPUT,
                    alignment=Alignment(vertical="center", indent=1))

        # Row 10: Table Column Headers
        headers = [
            "Category", "Assessment Deliverable", "Weight %", "Max Pts",
            "Earned Pts ✍️", "Score %", "Weighted Earned %", "Due Date", "Status", "Hurdle / Notes"
        ]
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=10, column=col_idx, value=h)
            cell.fill = FILL_NAVY_HEADER
            cell.font = F_TH
            align_h = "center" if col_idx in [1, 5, 6, 7, 8, 9] else ("right" if col_idx in [3, 4] else "left")
            cell.alignment = Alignment(horizontal=align_h, vertical="center", wrap_text=True)
            cell.border = BORDER_CELL

        # Populate Items (Starts at Row 11)
        row_idx = 11
        category_row_ranges = {}

        for cat in c["categories"]:
            cat_start = row_idx
            cat_id = cat["category_id"]
            cat_name = cat["name"]

            for item in cat["items"]:
                ws.row_dimensions[row_idx].height = 20
                is_zebra = (row_idx % 2 == 0)
                row_fill = FILL_ZEBRA if is_zebra else FILL_WHITE

                # Col A: Category
                c_cell = ws.cell(row=row_idx, column=1, value=cat_name)
                c_cell.font = Font(name=FONT_NAME, size=9, color="64748B")
                c_cell.fill = row_fill
                c_cell.border = BORDER_CELL
                c_cell.alignment = Alignment(vertical="center")

                # Col B: Assessment Deliverable
                b_cell = ws.cell(row=row_idx, column=2, value=item["name"])
                b_cell.font = F_DATA_BOLD
                b_cell.fill = row_fill
                b_cell.border = BORDER_CELL
                b_cell.alignment = Alignment(vertical="center")

                # Col C: Weight %
                w_cell = ws.cell(row=row_idx, column=3, value=item["weight_percent"] / 100.0)
                w_cell.number_format = "0.0%"
                w_cell.font = F_DATA
                w_cell.fill = row_fill
                w_cell.border = BORDER_CELL
                w_cell.alignment = Alignment(horizontal="right", vertical="center")

                # Col D: Max Pts
                m_cell = ws.cell(row=row_idx, column=4, value=item["max_points"])
                m_cell.font = F_DATA
                m_cell.fill = row_fill
                m_cell.border = BORDER_CELL
                m_cell.alignment = Alignment(horizontal="right", vertical="center")

                # Col E: Earned Pts [EDITABLE INPUT CELL - Highlighted in Soft Blue]
                e_cell = ws.cell(row=row_idx, column=5, value=item.get("earned_points"))
                e_cell.font = F_INPUT
                e_cell.fill = FILL_INPUT
                e_cell.border = BORDER_INPUT
                e_cell.alignment = Alignment(horizontal="right", vertical="center")

                # Col F: Score % Formula =IF(OR(ISBLANK(E11), E11=""), "", E11/D11)
                s_cell = ws.cell(row=row_idx, column=6, value=f'=IF(OR(ISBLANK(E{row_idx}), E{row_idx}=""), "", E{row_idx}/D{row_idx})')
                s_cell.number_format = "0.0%"
                s_cell.font = F_DATA
                s_cell.fill = row_fill
                s_cell.border = BORDER_CELL
                s_cell.alignment = Alignment(horizontal="right", vertical="center")

                # Col G: Weighted Earned % Formula =IF(OR(ISBLANK(E11), E11=""), "", F11*C11)
                we_cell = ws.cell(row=row_idx, column=7, value=f'=IF(OR(ISBLANK(E{row_idx}), E{row_idx}=""), "", F{row_idx}*C{row_idx})')
                we_cell.number_format = "0.00%"
                we_cell.font = F_DATA_BOLD
                we_cell.fill = row_fill
                we_cell.border = BORDER_CELL
                we_cell.alignment = Alignment(horizontal="right", vertical="center")

                # Col H: Due Date
                d_cell = ws.cell(row=row_idx, column=8, value=item.get("due_date") or "TBA")
                d_cell.font = F_DATA
                d_cell.fill = row_fill
                d_cell.border = BORDER_CELL
                d_cell.alignment = Alignment(horizontal="center", vertical="center")

                # Col I: Status pill
                st_val = item.get("status") or "Not Started"
                st_cell = ws.cell(row=row_idx, column=9, value=st_val)
                st_cell.border = BORDER_CELL
                st_cell.alignment = Alignment(horizontal="center", vertical="center")
                if st_val == "Done":
                    st_cell.fill = FILL_DONE
                    st_cell.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_DONE_TXT)
                elif st_val == "In Progress":
                    st_cell.fill = FILL_PROG
                    st_cell.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_PROG_TXT)
                else:
                    st_cell.fill = FILL_TODO
                    st_cell.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_TODO_TXT)

                # Col J: Hurdle / Notes
                is_hurdle = ("test" in cat_id.lower()) or ("midterm" in cat_id.lower()) or ("final" in cat_id.lower())
                note_val = "Mandatory Test Hurdle (>=50%)" if is_hurdle else ""
                n_cell = ws.cell(row=row_idx, column=10, value=note_val)
                n_cell.font = Font(name=FONT_NAME, size=8.5, italic=True, color="92400E" if is_hurdle else "64748B")
                n_cell.fill = row_fill
                n_cell.border = BORDER_CELL
                n_cell.alignment = Alignment(vertical="center")

                row_idx += 1

            category_row_ranges[cat_id] = (cat_start, row_idx - 1)

        end_item_row = row_idx - 1

        # Table Summary Row (Accounting Style with Double Bottom Border)
        ws.row_dimensions[row_idx].height = 22
        ws.merge_cells(f"A{row_idx}:B{row_idx}")
        ws[f"A{row_idx}"] = "COURSE TOTAL & WEIGHTS"
        style_range(ws, f"A{row_idx}:B{row_idx}", font=F_TOTAL, fill=FILL_TOTAL, border=BORDER_TOTAL,
                    alignment=Alignment(horizontal="right", vertical="center"))

        # Col C: Total Weight % (SUM)
        tw_cell = ws.cell(row=row_idx, column=3, value=f"=SUM(C11:C{end_item_row})")
        tw_cell.number_format = "0.0%"
        tw_cell.font = F_TOTAL
        tw_cell.fill = FILL_TOTAL
        tw_cell.border = BORDER_TOTAL
        tw_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col D: Total Max Points
        tm_cell = ws.cell(row=row_idx, column=4, value=f"=SUM(D11:D{end_item_row})")
        tm_cell.font = F_TOTAL
        tm_cell.fill = FILL_TOTAL
        tm_cell.border = BORDER_TOTAL
        tm_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col E: Total Earned Points
        te_cell = ws.cell(row=row_idx, column=5, value=f"=SUM(E11:E{end_item_row})")
        te_cell.font = F_TOTAL
        te_cell.fill = FILL_TOTAL
        te_cell.border = BORDER_TOTAL
        te_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col F: blank
        f_tot = ws.cell(row=row_idx, column=6, value="--")
        f_tot.font = F_TOTAL
        f_tot.fill = FILL_TOTAL
        f_tot.border = BORDER_TOTAL
        f_tot.alignment = Alignment(horizontal="center", vertical="center")

        # Col G: Total Weighted Earned %
        tg_cell = ws.cell(row=row_idx, column=7, value=f"=SUM(G11:G{end_item_row})")
        tg_cell.number_format = "0.00%"
        tg_cell.font = F_TOTAL
        tg_cell.fill = FILL_TOTAL
        tg_cell.border = BORDER_TOTAL
        tg_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col H-J: blank fillers for summary row
        for c_filler in [8, 9, 10]:
            cl = ws.cell(row=row_idx, column=c_filler, value="")
            cl.fill = FILL_TOTAL
            cl.border = BORDER_TOTAL

        # ======================================================================
        # Top KPI Cards (Rows 5-7): 5 Symmetrical Cards Spanning Cols A to J
        # ======================================================================
        # Card 1: Completed Weight % (Cols A-B)
        cw_formula = f'=SUMIF(E11:E{end_item_row}, "<>", C11:C{end_item_row})'
        render_kpi_card(ws, 1, 5, "COMPLETED WEIGHT", cw_formula, "of 100.0% Course Total", num_format="0.0%")

        # Card 2: Weighted Earned % (Cols C-D)
        ew_formula = f'=SUM(G11:G{end_item_row})'
        render_kpi_card(ws, 3, 5, "WEIGHTED EARNED", ew_formula, "Points Accumulated", num_format="0.00%")

        # Card 3: Current Running Average % (Cols E-F)
        # Safe zero-error formula: =IF(A6>0, C6/A6, "--")
        ca_formula = f'=IF(A6>0, C6/A6, "--")'
        render_kpi_card(ws, 5, 5, "CURRENT AVERAGE", ca_formula, "Based on graded work", num_format="0.0%")

        # Card 4: Projected Final Grade % (Cols G-H)
        # Safe formula: =IF(A6>0, C6 + (1-A6)*E6, "--")
        pf_formula = f'=IF(A6>0, C6 + (1-A6)*E6, "--")'
        render_kpi_card(ws, 7, 5, "PROJECTED FINAL", pf_formula, "Assuming current pace", num_format="0.0%")

        # Card 5: Passing Hurdle Compliance (Cols I-J)
        # Identifies test ranges to monitor >=50% average
        test_ranges = []
        for cat_id, (s_r, e_r) in category_row_ranges.items():
            if any(k in cat_id.lower() for k in ["test", "midterm", "final"]):
                test_ranges.append((s_r, e_r))

        if test_ranges:
            # Build safe check across all test categories
            s_first = test_ranges[0][0]
            e_last = test_ranges[-1][1]
            hurdle_formula = (
                f'=IF(SUMIF(E{s_first}:E{e_last}, "<>", C{s_first}:C{e_last})<=0, "PENDING", '
                f'IF(SUM(G{s_first}:G{e_last})/SUMIF(E{s_first}:E{e_last}, "<>", C{s_first}:C{e_last})>=0.5, '
                f'"ON TRACK (PASSED)", "⚠️ WARNING: <50%"))'
            )
            hurdle_sub = "Must score >=50% on Tests"
        else:
            hurdle_formula = '=IF(A6>0, IF(E6>=0.5, "ON TRACK (PASSED)", "NEEDS ATTENTION"), "PENDING")'
            hurdle_sub = "Overall >=50% to Pass"

        render_kpi_card(ws, 9, 5, "HURDLE COMPLIANCE", hurdle_formula, hurdle_sub)

        # Store sheet references for Master Dashboard
        course_sheet_meta[code] = {
            "title": c["course_name"],
            "credits": c["credits"],
            "is_technical": c["is_technical"],
            "grading_type": c["grading_type"],
            "completed_ref": f"'{code}'!A6",
            "earned_ref": f"'{code}'!C6",
            "current_avg_ref": f"'{code}'!E6",
            "projected_ref": f"'{code}'!G6",
            "hurdle_ref": f"'{code}'!I6"
        }

        auto_fit_columns(ws, min_width=12)

    # ==============================================================================
    # 2. Master "Dashboard & GPA" Tab (Executive Overview)
    # ==============================================================================
    ws_dash = wb.create_sheet(title="Dashboard & GPA", index=0)
    ws_dash.views.sheetView[0].showGridLines = True
    ws_dash.freeze_panes = "A11"

    # Layout Row Heights
    ws_dash.row_dimensions[1].height = 24
    ws_dash.row_dimensions[2].height = 18
    ws_dash.row_dimensions[3].height = 20
    ws_dash.row_dimensions[4].height = 8
    ws_dash.row_dimensions[5].height = 16
    ws_dash.row_dimensions[6].height = 26
    ws_dash.row_dimensions[7].height = 16
    ws_dash.row_dimensions[8].height = 8
    ws_dash.row_dimensions[9].height = 6
    ws_dash.row_dimensions[10].height = 26

    # Row 1-3 Title Block
    ws_dash.merge_cells("A1:J1")
    ws_dash["A1"] = "Seneca Polytechnic — Computer Systems Technology (CTY)"
    ws_dash["A1"].font = F_TITLE
    ws_dash["A1"].alignment = Alignment(vertical="center")

    ws_dash.merge_cells("A2:J2")
    ws_dash["A2"] = "Semester 3 Academic Performance Dashboard, Hurdle Verification & Official Seneca 4.0 GPA Calculator"
    ws_dash["A2"].font = F_SUBTITLE
    ws_dash["A2"].alignment = Alignment(vertical="center")

    ws_dash.merge_cells("A3:J3")
    ws_dash["A3"] = "💡 FAST NAVIGATION: Click any blue Course Code below to jump directly to that course sheet. Enter your grades to see GPA and totals update in real time."
    style_range(ws_dash, "A3:J3", font=Font(name=FONT_NAME, size=8.5, italic=True, color=C_INPUT_TEXT),
                fill=FILL_NOTICE, border=BORDER_INPUT,
                alignment=Alignment(vertical="center", indent=1))

    # Top KPI Cards (Rows 5-7): 5 Cards Spanning Cols A to J
    # Card 1 (Cols A-B): Cumulative GPA (Graded courses to date)
    # Uses helper column K (Quality Points = GPA * Credits)
    gpa_formula = '=IF(SUMIF(I11:I17, ">=0", C11:C17)>0, ROUND(SUM(K11:K17)/SUMIF(I11:I17, ">=0", C11:C17), 2), "--")'
    render_kpi_card(ws_dash, 1, 5, "CUMULATIVE GPA", gpa_formula, "Graded Courses to Date", num_format="0.00")

    # Card 2 (Cols C-D): Projected GPA (Using projected grades)
    # Uses helper column L (Projected Quality Points)
    proj_gpa_formula = '=IF(SUMIF(G11:G17, ">0", C11:C17)>0, ROUND(SUM(L11:L17)/SUMIF(G11:G17, ">0", C11:C17), 2), "--")'
    render_kpi_card(ws_dash, 3, 5, "PROJECTED GPA", proj_gpa_formula, "Estimated Final Term GPA", num_format="0.00")

    # Card 3 (Cols E-F): Current Overall Weighted Average %
    # Uses helper column M (Current Weighted Points = Avg * Credits)
    ov_avg_formula = '=IF(SUMIF(F11:F17, ">0", C11:C17)>0, ROUND(SUM(M11:M17)/SUMIF(F11:F17, ">0", C11:C17), 1), "--")'
    render_kpi_card(ws_dash, 5, 5, "CURRENT OVERALL AVG", ov_avg_formula, "Credit-Weighted Average", num_format="0.0%")

    # Card 4 (Cols G-H): Technical Major Average % (Computing Core Courses)
    # Uses helper columns N and O
    tech_avg_formula = '=IF(SUM(O11:O17)>0, ROUND(SUM(N11:N17)/SUM(O11:O17), 1), "--")'
    render_kpi_card(ws_dash, 7, 5, "TECHNICAL CORE AVG", tech_avg_formula, "5 Computing Core Courses", num_format="0.0%")

    # Card 5 (Cols I-J): Total Academic Credits
    render_kpi_card(ws_dash, 9, 5, "TOTAL TERM CREDITS", "=SUM(C11:C17)", "7 Enrolled Courses", num_format="0.0")

    # Table Column Headers (Row 10)
    dash_headers = [
        "Course Code", "Course Title", "Credits", "Classification",
        "Completed %", "Current Avg %", "Projected Final %", "Letter Grade", "GPA Points", "Hurdle Status"
    ]
    for col_idx, h in enumerate(dash_headers, 1):
        cell = ws_dash.cell(row=10, column=col_idx, value=h)
        cell.fill = FILL_NAVY_HEADER
        cell.font = F_TH
        align_h = "center" if col_idx in [1, 3, 5, 6, 7, 8, 9, 10] else "left"
        cell.alignment = Alignment(horizontal=align_h, vertical="center")
        cell.border = BORDER_CELL

    # Populate Course Rows (Rows 11 to 17)
    start_r = 11
    for idx, c in enumerate(courses):
        r = start_r + idx
        ws_dash.row_dimensions[r].height = 22
        code = c["course_code"]
        meta = course_sheet_meta[code]
        is_zebra = (r % 2 == 0)
        r_fill = FILL_ZEBRA if is_zebra else FILL_WHITE

        # Col A: Course Code (CLICKABLE HYPERLINK)
        code_cell = ws_dash.cell(row=r, column=1, value=f'=HYPERLINK("#\'{code}\'!A1", "{code}")')
        code_cell.font = F_LINK
        code_cell.fill = r_fill
        code_cell.border = BORDER_CELL
        code_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Col B: Course Title
        t_cell = ws_dash.cell(row=r, column=2, value=meta["title"])
        t_cell.font = F_DATA_BOLD
        t_cell.fill = r_fill
        t_cell.border = BORDER_CELL
        t_cell.alignment = Alignment(vertical="center")

        # Col C: Credits
        cr_cell = ws_dash.cell(row=r, column=3, value=meta["credits"])
        cr_cell.font = F_DATA
        cr_cell.fill = r_fill
        cr_cell.border = BORDER_CELL
        cr_cell.alignment = Alignment(horizontal="center", vertical="center")
        cr_cell.number_format = "0.0"

        # Col D: Classification
        type_str = "Technical Core" if meta["is_technical"] else ("Co-op Prep" if meta["grading_type"] == "sat_un" else "General Ed")
        type_cell = ws_dash.cell(row=r, column=4, value=type_str)
        type_cell.font = F_DATA
        type_cell.fill = r_fill
        type_cell.border = BORDER_CELL
        type_cell.alignment = Alignment(vertical="center")

        # Col E: Completed Weight %
        comp_cell = ws_dash.cell(row=r, column=5, value=f"={meta['completed_ref']}")
        comp_cell.number_format = "0.0%"
        comp_cell.font = F_DATA
        comp_cell.fill = r_fill
        comp_cell.border = BORDER_CELL
        comp_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col F: Current Avg % (Safe: returns blank if no completed grades)
        cur_cell = ws_dash.cell(row=r, column=6, value=f"=IF({meta['completed_ref']}>0, {meta['current_avg_ref']}, \"\")")
        cur_cell.number_format = "0.0%"
        cur_cell.font = F_DATA_BOLD
        cur_cell.fill = r_fill
        cur_cell.border = BORDER_CELL
        cur_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col G: Projected Final % (Safe: returns blank if no completed grades)
        proj_cell = ws_dash.cell(row=r, column=7, value=f"=IF({meta['completed_ref']}>0, {meta['projected_ref']}, \"\")")
        proj_cell.number_format = "0.0%"
        proj_cell.font = F_DATA_BOLD
        proj_cell.fill = r_fill
        proj_cell.border = BORDER_CELL
        proj_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col H: Letter Grade (Official Seneca Scale: A+, A, B+, B, C+, C, D+, D, F or SAT/UN)
        if meta["grading_type"] == "sat_un":
            lg_formula = f'=IF({meta["completed_ref"]}>0, IF({meta["current_avg_ref"]}>=0.8, "SAT", "UN"), "--")'
        else:
            lg_formula = (
                f'=IF(ISNUMBER(G{r}), '
                f'IF(G{r}>=0.9, "A+", IF(G{r}>=0.8, "A", IF(G{r}>=0.75, "B+", '
                f'IF(G{r}>=0.7, "B", IF(G{r}>=0.65, "C+", IF(G{r}>=0.6, "C", '
                f'IF(G{r}>=0.55, "D+", IF(G{r}>=0.5, "D", "F")))))))), "--")'
            )
        lg_cell = ws_dash.cell(row=r, column=8, value=lg_formula)
        lg_cell.font = F_DATA_BOLD
        lg_cell.fill = r_fill
        lg_cell.border = BORDER_CELL
        lg_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Col I: GPA Points (A+/A=4.0, B+=3.5, B=3.0, C+=2.5, C=2.0, D+=1.5, D=1.0, F=0.0)
        if meta["grading_type"] == "sat_un":
            gpa_formula = '""'
        else:
            gpa_formula = (
                f'=IF(H{r}="A+", 4.0, IF(H{r}="A", 4.0, IF(H{r}="B+", 3.5, '
                f'IF(H{r}="B", 3.0, IF(H{r}="C+", 2.5, IF(H{r}="C", 2.0, '
                f'IF(H{r}="D+", 1.5, IF(H{r}="D", 1.0, IF(H{r}="F", 0.0, "")))))))))'
            )
        gpa_cell = ws_dash.cell(row=r, column=9, value=gpa_formula)
        gpa_cell.number_format = "0.0"
        gpa_cell.font = F_DATA_BOLD
        gpa_cell.fill = r_fill
        gpa_cell.border = BORDER_CELL
        gpa_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col J: Hurdle Status Reference
        h_cell = ws_dash.cell(row=r, column=10, value=f"={meta['hurdle_ref']}")
        h_cell.font = F_DATA_BOLD
        h_cell.fill = r_fill
        h_cell.border = BORDER_CELL
        h_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Hidden / Discreet Helper Columns (Cols K to O) for 100% Robust Math
        # Col K: Quality Points = GPA * Credits
        ws_dash.cell(row=r, column=11, value=f'=IF(ISNUMBER(I{r}), I{r}*C{r}, "")')
        # Col L: Projected Quality Points
        ws_dash.cell(row=r, column=12, value=f'=IF(ISNUMBER(G{r}), IF(G{r}>=0.9, 4.0, IF(G{r}>=0.8, 4.0, IF(G{r}>=0.75, 3.5, IF(G{r}>=0.7, 3.0, IF(G{r}>=0.65, 2.5, IF(G{r}>=0.6, 2.0, IF(G{r}>=0.55, 1.5, IF(G{r}>=0.5, 1.0, 0.0))))))))*C{r}, "")')
        # Col M: Current Weighted Pts = Col F * Col C
        ws_dash.cell(row=r, column=13, value=f'=IF(AND(ISNUMBER(F{r}), F{r}>0), F{r}*C{r}, "")')
        # Col N: Tech Weighted Pts
        ws_dash.cell(row=r, column=14, value=f'=IF(AND(D{r}="Technical Core", ISNUMBER(F{r}), F{r}>0), F{r}*C{r}, "")')
        # Col O: Tech Credits
        ws_dash.cell(row=r, column=15, value=f'=IF(AND(D{r}="Technical Core", ISNUMBER(F{r}), F{r}>0), C{r}, "")')

    end_dash_row = start_r + len(courses) - 1

    # Semester Summary Row (Row 18)
    summary_r = end_dash_row + 1
    ws_dash.row_dimensions[summary_r].height = 22
    ws_dash.merge_cells(f"A{summary_r}:B{summary_r}")
    ws_dash[f"A{summary_r}"] = "SEMESTER 3 WEIGHTED TOTALS"
    style_range(ws_dash, f"A{summary_r}:B{summary_r}", font=F_TOTAL, fill=FILL_TOTAL, border=BORDER_TOTAL,
                alignment=Alignment(horizontal="right", vertical="center"))

    # Col C: Total Credits
    s_cr = ws_dash.cell(row=summary_r, column=3, value=f"=SUM(C{start_r}:C{end_dash_row})")
    s_cr.number_format = "0.0"
    s_cr.font = F_TOTAL
    s_cr.fill = FILL_TOTAL
    s_cr.border = BORDER_TOTAL
    s_cr.alignment = Alignment(horizontal="center", vertical="center")

    # Col D: Blank
    ws_dash.cell(row=summary_r, column=4, value="--").fill = FILL_TOTAL
    ws_dash.cell(row=summary_r, column=4).border = BORDER_TOTAL
    ws_dash.cell(row=summary_r, column=4).alignment = Alignment(horizontal="center", vertical="center")

    # Col E: Average Completed %
    s_comp = ws_dash.cell(row=summary_r, column=5, value=f"=AVERAGE(E{start_r}:E{end_dash_row})")
    s_comp.number_format = "0.0%"
    s_comp.font = F_TOTAL
    s_comp.fill = FILL_TOTAL
    s_comp.border = BORDER_TOTAL
    s_comp.alignment = Alignment(horizontal="right", vertical="center")

    # Col F: Overall Current Avg
    s_cur = ws_dash.cell(row=summary_r, column=6, value="=E6")
    s_cur.number_format = "0.0%"
    s_cur.font = F_TOTAL
    s_cur.fill = FILL_TOTAL
    s_cur.border = BORDER_TOTAL
    s_cur.alignment = Alignment(horizontal="right", vertical="center")

    # Col G: Overall Projected Final
    s_proj = ws_dash.cell(row=summary_r, column=7, value="=C6")
    s_proj.number_format = "0.0%"
    s_proj.font = F_TOTAL
    s_proj.fill = FILL_TOTAL
    s_proj.border = BORDER_TOTAL
    s_proj.alignment = Alignment(horizontal="right", vertical="center")

    # Col H: Projected Term Grade
    s_lg = ws_dash.cell(row=summary_r, column=8, value='=IF(ISNUMBER(G6), IF(G6>=0.9, "A+", IF(G6>=0.8, "A", IF(G6>=0.75, "B+", IF(G6>=0.7, "B", IF(G6>=0.65, "C+", IF(G6>=0.6, "C", IF(G6>=0.55, "D+", IF(G6>=0.5, "D", "F")))))))), "--")')
    s_lg.font = F_TOTAL
    s_lg.fill = FILL_TOTAL
    s_lg.border = BORDER_TOTAL
    s_lg.alignment = Alignment(horizontal="center", vertical="center")

    # Col I: Cumulative Term GPA
    s_gpa = ws_dash.cell(row=summary_r, column=9, value="=A6")
    s_gpa.number_format = "0.00"
    s_gpa.font = F_TOTAL
    s_gpa.fill = FILL_TOTAL
    s_gpa.border = BORDER_TOTAL
    s_gpa.alignment = Alignment(horizontal="right", vertical="center")

    # Col J: Hurdle Action Watch
    s_h = ws_dash.cell(row=summary_r, column=10, value=f'=IF(COUNTIF(J{start_r}:J{end_dash_row}, "*WARNING*")>0, "⚠️ ACTION REQUIRED", "ALL CLEAR")')
    s_h.font = F_TOTAL
    s_h.fill = FILL_TOTAL
    s_h.border = BORDER_TOTAL
    s_h.alignment = Alignment(horizontal="center", vertical="center")

    # ==============================================================================
    # Rows 21-30: Official Seneca Grading Scale Reference & Hurdle Legend
    # ==============================================================================
    ws_dash.merge_cells("A21:E21")
    ws_dash["A21"] = "OFFICIAL SENECA POLYTECHNIC GRADING SCALE (4.0 SCALE)"
    style_range(ws_dash, "A21:E21", font=Font(name=FONT_NAME, size=9, bold=True, color=C_WHITE),
                fill=FILL_NAVY_HEADER, border=BORDER_CELL, alignment=Alignment(horizontal="center", vertical="center"))

    ws_dash.merge_cells("G21:J21")
    ws_dash["G21"] = "SEMESTER 3 ACADEMIC POLICY & HURDLE SUMMARY"
    style_range(ws_dash, "G21:J21", font=Font(name=FONT_NAME, size=9, bold=True, color=C_WHITE),
                fill=FILL_NAVY_HEADER, border=BORDER_CELL, alignment=Alignment(horizontal="center", vertical="center"))

    scale_data = [
        ("A+", "90% - 100%", "4.0", "Exemplary Performance"),
        ("A",  "80% - 89%",  "4.0", "Excellent Comprehension"),
        ("B+", "75% - 79%",  "3.5", "Very Good Standing"),
        ("B",  "70% - 74%",  "3.0", "Good Standing"),
        ("C+", "65% - 69%",  "2.5", "Satisfactory Achievement"),
        ("C",  "60% - 64%",  "2.0", "Minimum Technical Prerequisite"),
        ("D+", "55% - 59%",  "1.5", "Marginal Pass"),
        ("D",  "50% - 54%",  "1.0", "Minimum Course Pass"),
        ("F",  "0% - 49%",   "0.0", "Unsatisfactory / Course Failure"),
    ]

    for s_idx, (grd, pct_rng, pts, desc) in enumerate(scale_data):
        r_scale = 22 + s_idx
        ws_dash.row_dimensions[r_scale].height = 18
        ws_dash.cell(row=r_scale, column=1, value=grd).font = F_DATA_BOLD
        ws_dash.cell(row=r_scale, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws_dash.cell(row=r_scale, column=1).border = BORDER_CELL

        ws_dash.cell(row=r_scale, column=2, value=pct_rng).font = F_DATA
        ws_dash.cell(row=r_scale, column=2).alignment = Alignment(horizontal="center", vertical="center")
        ws_dash.cell(row=r_scale, column=2).border = BORDER_CELL

        ws_dash.cell(row=r_scale, column=3, value=float(pts)).font = F_DATA_BOLD
        ws_dash.cell(row=r_scale, column=3).alignment = Alignment(horizontal="center", vertical="center")
        ws_dash.cell(row=r_scale, column=3).number_format = "0.0"
        ws_dash.cell(row=r_scale, column=3).border = BORDER_CELL

        ws_dash.merge_cells(f"D{r_scale}:E{r_scale}")
        ws_dash.cell(row=r_scale, column=4, value=desc).font = Font(name=FONT_NAME, size=8.5, color="64748B")
        style_range(ws_dash, f"D{r_scale}:E{r_scale}", border=BORDER_CELL, alignment=Alignment(vertical="center", indent=1))

    # Academic Policy Legend (Right Box G22:J30)
    policy_texts = [
        "1. Dual-Criterion Hurdle: CSN305, DAT330, MST300 & SEC320 require a weighted average of >=50% on all tests/exams combined to obtain course credit.",
        "2. Lab Completion Hurdle: All lab exercises must be satisfactorily submitted and verified for technical course passing.",
        "3. Technical Core Isolation: 5 core computing courses (CSN305, DAT330, MST300, SEC320, OPS345) are tracked separately from General Electives.",
        "4. Non-GPA Co-op Course: WTP100 is graded on a Satisfactory/Unsatisfactory (SAT/UN) basis. All 14 Knowledge Checks must achieve >=80%."
    ]

    for p_idx, p_text in enumerate(policy_texts):
        r_p_start = 22 + (p_idx * 2)
        ws_dash.merge_cells(f"G{r_p_start}:J{r_p_start+1}")
        ws_dash.cell(row=r_p_start, column=7, value=p_text).font = Font(name=FONT_NAME, size=8.5, color=C_NAVY_DARK)
        style_range(ws_dash, f"G{r_p_start}:J{r_p_start+1}", border=BORDER_CELL, fill=FILL_CARD,
                    alignment=Alignment(vertical="center", wrap_text=True))

    auto_fit_columns(ws_dash, min_width=12)

    # ==============================================================================
    # 3. "What-If Simulator" Tab
    # ==============================================================================
    ws_wi = wb.create_sheet(title="What-If Simulator")
    ws_wi.views.sheetView[0].showGridLines = True
    ws_wi.freeze_panes = "A11"

    ws_wi.row_dimensions[1].height = 24
    ws_wi.row_dimensions[2].height = 18
    ws_wi.row_dimensions[3].height = 20
    ws_wi.row_dimensions[4].height = 8
    ws_wi.row_dimensions[5].height = 16
    ws_wi.row_dimensions[6].height = 26
    ws_wi.row_dimensions[7].height = 16
    ws_wi.row_dimensions[8].height = 8
    ws_wi.row_dimensions[9].height = 20
    ws_wi.row_dimensions[10].height = 26

    # Title
    ws_wi.merge_cells("A1:H1")
    ws_wi["A1"] = "What-If Final Grade Simulator & Academic Target Solver"
    ws_wi["A1"].font = F_TITLE
    ws_wi["A1"].alignment = Alignment(vertical="center")

    ws_wi.merge_cells("I1:K1")
    ws_wi["I1"] = '=HYPERLINK("#\'Dashboard & GPA\'!A1", "⬅ Back to Dashboard")'
    style_range(ws_wi, "I1:K1", font=Font(name=FONT_NAME, size=9.5, bold=True, color=C_WHITE),
                fill=FILL_NAVY_HEADER, border=BORDER_CELL,
                alignment=Alignment(horizontal="center", vertical="center"))

    ws_wi.merge_cells("A2:K2")
    ws_wi["A2"] = "Simulate required scores on uncompleted assignments, midterms, and final exams to achieve desired target letter grades"
    ws_wi["A2"].font = F_SUBTITLE
    ws_wi["A2"].alignment = Alignment(vertical="center")

    ws_wi.merge_cells("A3:K3")
    ws_wi["A3"] = "💡 TARGET SOLVER: Change your Target Letter Grade in Column G (blue shaded cells) to see the exact average needed on remaining coursework."
    style_range(ws_wi, "A3:K3", font=Font(name=FONT_NAME, size=8.5, italic=True, color=C_INPUT_TEXT),
                fill=FILL_NOTICE, border=BORDER_INPUT,
                alignment=Alignment(vertical="center", indent=1))

    # Top KPI Cards for What-If
    render_kpi_card(ws_wi, 1, 5, "CURRENT GPA", "='Dashboard & GPA'!A6", "Based on completed work", num_format="0.00")
    render_kpi_card(ws_wi, 3, 5, "PROJECTED GPA", "='Dashboard & GPA'!C6", "At current performance pace", num_format="0.00")
    render_kpi_card(ws_wi, 5, 5, "TARGET ACHIEVABLE", '=COUNTIF(K11:K16, "*Achievable*")', "Courses within reach")
    render_kpi_card(ws_wi, 7, 5, "CHALLENGING COURSES", '=COUNTIF(K11:K16, "*Challenging*")', "Requires >=85% on remainder")
    render_kpi_card(ws_wi, 9, 5, "CRITICAL WATCH", '=COUNTIF(K11:K16, "*Impossible*")', "Statistically Out of Reach")

    # Table Headers
    wi_headers = [
        "Course Code", "Course Title", "Credits", "Completed %",
        "Earned Weight %", "Current Avg %", "Target Grade ✍️", "Target %",
        "Remaining Weight %", "Required % on Remainder", "Feasibility Assessment"
    ]
    for col_idx, h in enumerate(wi_headers, 1):
        cell = ws_wi.cell(row=10, column=col_idx, value=h)
        cell.fill = FILL_NAVY_HEADER
        cell.font = F_TH
        align_h = "center" if col_idx in [1, 3, 4, 5, 6, 7, 8, 9, 10, 11] else "left"
        cell.alignment = Alignment(horizontal=align_h, vertical="center")
        cell.border = BORDER_CELL

    # Populate Graded Courses
    graded_courses = [c for c in courses if c["grading_type"] == "percentage_gpa"]
    for idx, c in enumerate(graded_courses):
        r = 11 + idx
        ws_wi.row_dimensions[r].height = 22
        code = c["course_code"]
        meta = course_sheet_meta[code]
        is_zebra = (r % 2 == 0)
        r_fill = FILL_ZEBRA if is_zebra else FILL_WHITE

        # Col A: Course Code Hyperlink
        ws_wi.cell(row=r, column=1, value=f'=HYPERLINK("#\'{code}\'!A1", "{code}")').font = F_LINK
        ws_wi.cell(row=r, column=1).fill = r_fill
        ws_wi.cell(row=r, column=1).border = BORDER_CELL
        ws_wi.cell(row=r, column=1).alignment = Alignment(horizontal="center", vertical="center")

        # Col B: Course Title
        ws_wi.cell(row=r, column=2, value=meta["title"]).font = F_DATA_BOLD
        ws_wi.cell(row=r, column=2).fill = r_fill
        ws_wi.cell(row=r, column=2).border = BORDER_CELL
        ws_wi.cell(row=r, column=2).alignment = Alignment(vertical="center")

        # Col C: Credits
        ws_wi.cell(row=r, column=3, value=meta["credits"]).font = F_DATA
        ws_wi.cell(row=r, column=3).fill = r_fill
        ws_wi.cell(row=r, column=3).border = BORDER_CELL
        ws_wi.cell(row=r, column=3).alignment = Alignment(horizontal="center", vertical="center")

        # Col D: Completed Weight %
        cw_cell = ws_wi.cell(row=r, column=4, value=f"={meta['completed_ref']}")
        cw_cell.number_format = "0.0%"
        cw_cell.font = F_DATA
        cw_cell.fill = r_fill
        cw_cell.border = BORDER_CELL
        cw_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col E: Earned Weight %
        ew_cell = ws_wi.cell(row=r, column=5, value=f"={meta['earned_ref']}")
        ew_cell.number_format = "0.00%"
        ew_cell.font = F_DATA
        ew_cell.fill = r_fill
        ew_cell.border = BORDER_CELL
        ew_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col F: Current Avg %
        ca_cell = ws_wi.cell(row=r, column=6, value=f"=IF({meta['completed_ref']}>0, {meta['current_avg_ref']}, \"--\")")
        ca_cell.number_format = "0.0%"
        ca_cell.font = F_DATA_BOLD
        ca_cell.fill = r_fill
        ca_cell.border = BORDER_CELL
        ca_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col G: Target Grade [INPUT CELL - Default: A]
        tg_cell = ws_wi.cell(row=r, column=7, value="A")
        tg_cell.font = F_INPUT
        tg_cell.fill = FILL_INPUT
        tg_cell.border = BORDER_INPUT
        tg_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Col H: Target % Formula
        tp_formula = (
            f'=IF(G{r}="A+", 0.90, IF(G{r}="A", 0.80, IF(G{r}="B+", 0.75, '
            f'IF(G{r}="B", 0.70, IF(G{r}="C+", 0.65, IF(G{r}="C", 0.60, '
            f'IF(G{r}="D+", 0.55, IF(G{r}="D", 0.50, 0.50))))))))'
        )
        tp_cell = ws_wi.cell(row=r, column=8, value=tp_formula)
        tp_cell.number_format = "0.0%"
        tp_cell.font = F_DATA_BOLD
        tp_cell.fill = r_fill
        tp_cell.border = BORDER_CELL
        tp_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col I: Remaining Weight % = 1.0 - Completed Weight (Col D)
        rw_cell = ws_wi.cell(row=r, column=9, value=f"=1.0-D{r}")
        rw_cell.number_format = "0.0%"
        rw_cell.font = F_DATA
        rw_cell.fill = r_fill
        rw_cell.border = BORDER_CELL
        rw_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col J: Required Avg on Remaining Deliverables
        req_formula = f'=IF(I{r}<=0, "Finished", (H{r}-E{r})/I{r})'
        req_cell = ws_wi.cell(row=r, column=10, value=req_formula)
        req_cell.number_format = "0.0%"
        req_cell.font = F_DATA_BOLD
        req_cell.fill = r_fill
        req_cell.border = BORDER_CELL
        req_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Col K: Feasibility Assessment
        feas_formula = (
            f'=IF(I{r}<=0, "Course Completed", '
            f'IF(J{r}<=0, "✅ Secured", '
            f'IF(J{r}>1.0, "❌ Impossible (>100%)", '
            f'IF(J{r}>=0.85, "⚠️ Challenging (>=85%)", "✅ Achievable"))))'
        )
        feas_cell = ws_wi.cell(row=r, column=11, value=feas_formula)
        feas_cell.font = F_DATA_BOLD
        feas_cell.fill = r_fill
        feas_cell.border = BORDER_CELL
        feas_cell.alignment = Alignment(horizontal="center", vertical="center")

    auto_fit_columns(ws_wi, min_width=12)

    # ==============================================================================
    # 4. "Timeline & Milestones" Tab
    # ==============================================================================
    ws_tl = wb.create_sheet(title="Timeline & Milestones")
    ws_tl.views.sheetView[0].showGridLines = True
    ws_tl.freeze_panes = "A6"

    ws_tl.row_dimensions[1].height = 24
    ws_tl.row_dimensions[2].height = 18
    ws_tl.row_dimensions[3].height = 20
    ws_tl.row_dimensions[4].height = 8
    ws_tl.row_dimensions[5].height = 26

    # Title
    ws_tl.merge_cells("A1:E1")
    ws_tl["A1"] = "Semester 3 Deliverables Chronological Timeline & Milestone Tracker"
    ws_tl["A1"].font = F_TITLE
    ws_tl["A1"].alignment = Alignment(vertical="center")

    ws_tl.merge_cells("F1:G1")
    ws_tl["F1"] = '=HYPERLINK("#\'Dashboard & GPA\'!A1", "⬅ Back to Dashboard")'
    style_range(ws_tl, "F1:G1", font=Font(name=FONT_NAME, size=9.5, bold=True, color=C_WHITE),
                fill=FILL_NAVY_HEADER, border=BORDER_CELL,
                alignment=Alignment(horizontal="center", vertical="center"))

    ws_tl.merge_cells("A2:G2")
    ws_tl["A2"] = "Master schedule of 110+ assignments, lab exercises, quizzes, midterms, and final exams sorted chronologically"
    ws_tl["A2"].font = F_SUBTITLE
    ws_tl["A2"].alignment = Alignment(vertical="center")

    ws_tl.merge_cells("A3:G3")
    ws_tl["A3"] = "💡 JUMP TO COURSE: Click 'Open Sheet ➔' on any deliverable to navigate directly to that course sheet."
    style_range(ws_tl, "A3:G3", font=Font(name=FONT_NAME, size=8.5, italic=True, color=C_INPUT_TEXT),
                fill=FILL_NOTICE, border=BORDER_INPUT,
                alignment=Alignment(vertical="center", indent=1))

    tl_headers = ["Course", "Assessment Deliverable", "Evaluation Category", "Weight %", "Scheduled Due Date", "Current Status", "Quick Link"]
    for col_idx, h in enumerate(tl_headers, 1):
        cell = ws_tl.cell(row=5, column=col_idx, value=h)
        cell.fill = FILL_NAVY_HEADER
        cell.font = F_TH
        align_h = "center" if col_idx in [1, 4, 5, 6, 7] else "left"
        cell.alignment = Alignment(horizontal=align_h, vertical="center")
        cell.border = BORDER_CELL

    # Gather items
    all_deliverables = []
    for c in courses:
        code = c["course_code"]
        for cat in c["categories"]:
            for item in cat["items"]:
                all_deliverables.append({
                    "course": code,
                    "name": item["name"],
                    "category": cat["name"],
                    "weight": item["weight_percent"],
                    "due_date": item.get("due_date") or "TBA",
                    "status": item.get("status") or "Not Started"
                })

    def date_sort_key(it):
        d = it["due_date"]
        if not d or d == "TBA":
            return "9999-99-99"
        parts = d.split("-")
        if len(parts) == 3:
            return f"{parts[0]:0>4}-{int(parts[1]):0>2}-{int(parts[2]):0>2}"
        return d

    all_deliverables.sort(key=date_sort_key)

    for idx, item in enumerate(all_deliverables):
        r = 6 + idx
        ws_tl.row_dimensions[r].height = 20
        is_zebra = (r % 2 == 0)
        r_fill = FILL_ZEBRA if is_zebra else FILL_WHITE

        # Col A: Course Code
        c_c = ws_tl.cell(row=r, column=1, value=item["course"])
        c_c.font = F_DATA_BOLD
        c_c.fill = r_fill
        c_c.border = BORDER_CELL
        c_c.alignment = Alignment(horizontal="center", vertical="center")

        # Col B: Deliverable Title
        d_c = ws_tl.cell(row=r, column=2, value=item["name"])
        d_c.font = F_DATA
        d_c.fill = r_fill
        d_c.border = BORDER_CELL
        d_c.alignment = Alignment(vertical="center")

        # Col C: Category
        cat_c = ws_tl.cell(row=r, column=3, value=item["category"])
        cat_c.font = Font(name=FONT_NAME, size=9, color="64748B")
        cat_c.fill = r_fill
        cat_c.border = BORDER_CELL
        cat_c.alignment = Alignment(vertical="center")

        # Col D: Weight %
        w_c = ws_tl.cell(row=r, column=4, value=item["weight"] / 100.0)
        w_c.number_format = "0.0%"
        w_c.font = F_DATA
        w_c.fill = r_fill
        w_c.border = BORDER_CELL
        w_c.alignment = Alignment(horizontal="right", vertical="center")

        # Col E: Due Date
        dt_c = ws_tl.cell(row=r, column=5, value=item["due_date"])
        dt_c.font = F_DATA
        dt_c.fill = r_fill
        dt_c.border = BORDER_CELL
        dt_c.alignment = Alignment(horizontal="center", vertical="center")

        # Col F: Status Pill
        st_val = item["status"]
        st_c = ws_tl.cell(row=r, column=6, value=st_val)
        st_c.border = BORDER_CELL
        st_c.alignment = Alignment(horizontal="center", vertical="center")
        if st_val == "Done":
            st_c.fill = FILL_DONE
            st_c.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_DONE_TXT)
        elif st_val == "In Progress":
            st_c.fill = FILL_PROG
            st_c.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_PROG_TXT)
        else:
            st_c.fill = FILL_TODO
            st_c.font = Font(name=FONT_NAME, size=8.5, bold=True, color=C_TODO_TXT)

        # Col G: Jump Link
        link_c = ws_tl.cell(row=r, column=7, value=f'=HYPERLINK("#\'{item["course"]}\'!A1", "Open Sheet ➔")')
        link_c.font = F_LINK
        link_c.fill = r_fill
        link_c.border = BORDER_CELL
        link_c.alignment = Alignment(horizontal="center", vertical="center")

    auto_fit_columns(ws_tl, min_width=12)

    # Save finalized workbook
    wb.save(output_file)
    print(f"[✓] Successfully generated executive '{output_file}' with {len(wb.sheetnames)} tabs:")
    for s in wb.sheetnames:
        print(f"    - {s}")

if __name__ == "__main__":
    generate_workbook()

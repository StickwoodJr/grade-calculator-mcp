#!/usr/bin/env python3
"""
Multi-Tab Grade Calculator Spreadsheet Generator.

Generates 'grade_calculator.xlsx' using openpyxl, pre-populated with
Seneca CTY Semester 3 courses. 100% compatible with Excel & Google Sheets.

Tabs:
  1. Dashboard & GPA (Overview, cumulative Seneca 4.0 GPA, technical vs overall avg, course table)
  2-8. Course Sheets (CSN305, DAT330, MST300, PSY262, SEC320, OPS345, WTP100)
  9. What-If Simulator (Target grade solver & required exam scores)
  10. Timeline & Milestones (Chronological assessment tracker)
"""

import json
import glob
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Design Palette
PRIMARY_COLOR = "1E293B"      # Dark Slate
HEADER_FILL = PatternFill(start_color=PRIMARY_COLOR, end_color=PRIMARY_COLOR, fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

SECTION_COLOR = "334155"
SECTION_FILL = PatternFill(start_color=SECTION_COLOR, end_color=SECTION_COLOR, fill_type="solid")
SECTION_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

CARD_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
ALERT_FILL = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
ALERT_FONT = Font(name="Calibri", size=11, bold=True, color="991B1B")

SUCCESS_FILL = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
SUCCESS_FONT = Font(name="Calibri", size=11, bold=True, color="166534")

BORDER_THIN = Side(border_style="thin", color="CBD5E1")
BOX_BORDER = Border(left=BORDER_THIN, right=BORDER_THIN, top=BORDER_THIN, bottom=BORDER_THIN)

TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="0F172A")
SUBTITLE_FONT = Font(name="Calibri", size=10, italic=True, color="64748B")
BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="0F172A")
REGULAR_FONT = Font(name="Calibri", size=11, color="1E293B")

def auto_adjust_column_widths(ws, min_width=12):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or '')
            if cell.number_format and '%' in cell.number_format:
                val += '%'
            max_len = max(max_len, len(val))
        ws.column_dimensions[col_letter].width = max(max_len + 4, min_width)

def generate_workbook(data_dir="data/courses", output_file="grade_calculator.xlsx"):
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Load course files
    with open(os.path.join(data_dir, "courses_index.json"), "r") as f:
        index_data = json.load(f)

    courses = []
    for c_info in index_data["courses"]:
        file_path = os.path.join(data_dir, c_info["file"])
        with open(file_path, "r") as f:
            courses.append(json.load(f))

    # ==========================================================
    # 1. Create Individual Course Tabs
    # ==========================================================
    course_sheet_meta = {}

    for c in courses:
        code = c["course_code"]
        ws = wb.create_sheet(title=code)
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = "A10"

        # Title Block
        ws["A1"] = f"{code}: {c['course_name']}"
        ws["A1"].font = TITLE_FONT
        tech_str = "Technical Computing Core" if c["is_technical"] else ("Co-op Preparation" if c["grading_type"] == "sat_un" else "General Elective")
        ws["A2"] = f"Credits: {c['credits']}  |  Classification: {tech_str}  |  Grading Scale: {c['grade_scale']}"
        ws["A2"].font = SUBTITLE_FONT

        # Passing Criteria Note
        criteria_str = "Passing Criteria: " + " • ".join(c.get("passing_criteria", []))
        ws["A3"] = criteria_str
        ws["A3"].font = Font(name="Calibri", size=9, italic=True, color="475569")

        # Summary KPIs Banner (Rows 5-7)
        labels = [
            ("B5", "Completed Weight", "C5"),
            ("D5", "Earned Weight", "E5"),
            ("F5", "Current Average", "G5"),
            ("H5", "Projected Final", "I5"),
            ("J5", "Hurdle Status", "K5")
        ]
        for lbl_pos, lbl_text, val_pos in labels:
            ws[lbl_pos] = lbl_text
            ws[lbl_pos].font = Font(name="Calibri", size=9, bold=True, color="475569")
            ws[lbl_pos].alignment = Alignment(horizontal="center")
            ws[val_pos].font = BOLD_FONT
            ws[val_pos].alignment = Alignment(horizontal="center")

        # Table Header (Row 9)
        headers = [
            "Category", "Assessment Item", "Weight %", "Max Pts",
            "Earned Pts", "Score %", "Weighted Earned %", "Due Date", "Status"
        ]
        for col_num, h in enumerate(headers, 1):
            cell = ws.cell(row=9, column=col_num, value=h)
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = BOX_BORDER

        # Populate Items
        row_idx = 10
        category_row_ranges = {}
        for cat in c["categories"]:
            cat_start = row_idx
            cat_id = cat["category_id"]
            cat_name = cat["name"]
            for item in cat["items"]:
                ws.cell(row=row_idx, column=1, value=cat_name).font = REGULAR_FONT
                ws.cell(row=row_idx, column=2, value=item["name"]).font = REGULAR_FONT
                
                # Weight %
                w_cell = ws.cell(row=row_idx, column=3, value=item["weight_percent"] / 100.0)
                w_cell.number_format = "0.0%"
                w_cell.font = REGULAR_FONT
                w_cell.alignment = Alignment(horizontal="right")

                # Max Points
                m_cell = ws.cell(row=row_idx, column=4, value=item["max_points"])
                m_cell.font = REGULAR_FONT
                m_cell.alignment = Alignment(horizontal="right")

                # Earned Points (Input cell)
                e_cell = ws.cell(row=row_idx, column=5, value=item.get("earned_points"))
                e_cell.font = BOLD_FONT
                e_cell.alignment = Alignment(horizontal="right")

                # Score % Formula =IF(ISBLANK(E10), "", E10/D10)
                s_cell = ws.cell(row=row_idx, column=6, value=f'=IF(ISBLANK(E{row_idx}), "", E{row_idx}/D{row_idx})')
                s_cell.number_format = "0.0%"
                s_cell.font = REGULAR_FONT
                s_cell.alignment = Alignment(horizontal="right")

                # Weighted Earned % Formula =IF(ISBLANK(E{row}), "", F{row}*C{row})
                we_cell = ws.cell(row=row_idx, column=7, value=f'=IF(ISBLANK(E{row_idx}), "", F{row_idx}*C{row_idx})')
                we_cell.number_format = "0.00%"
                we_cell.font = REGULAR_FONT
                we_cell.alignment = Alignment(horizontal="right")

                # Due Date & Status
                ws.cell(row=row_idx, column=8, value=item.get("due_date") or "").font = REGULAR_FONT
                st_cell = ws.cell(row=row_idx, column=9, value=item.get("status") or "Not Started")
                st_cell.font = REGULAR_FONT
                st_cell.alignment = Alignment(horizontal="center")

                for col_num in range(1, 10):
                    ws.cell(row=row_idx, column=col_num).border = BOX_BORDER

                row_idx += 1
            category_row_ranges[cat_id] = (cat_start, row_idx - 1)

        end_item_row = row_idx - 1

        # Completed Weight Formula (C5) =SUMIF(E10:E{end}, "<>", C10:C{end})
        ws["C5"] = f'=SUMIF(E10:E{end_item_row}, "<>", C10:C{end_item_row})'
        ws["C5"].number_format = "0.0%"

        # Earned Weight Formula (E5) =SUM(G10:G{end})
        ws["E5"] = f'=SUM(G10:G{end_item_row})'
        ws["E5"].number_format = "0.00%"

        # Current Average Formula (G5) =IF(C5>0, E5/C5, "N/A")
        ws["G5"] = f'=IF(C5>0, E5/C5, "N/A")'
        ws["G5"].number_format = "0.0%"

        # Projected Final Formula (I5) =IF(C5>0, E5+(1-C5)*G5, 1.0)
        ws["I5"] = f'=IF(C5>0, E5 + (1-C5)*G5, 1.0)'
        ws["I5"].number_format = "0.0%"

        # Hurdle Check Formula (K5)
        # Check if course has hurdles (e.g. tests >= 50%)
        hurdle_formulas = []
        for h in c.get("hurdles", []):
            if h.get("type") == "category_average" and h.get("target_category") in category_row_ranges:
                h_cat = h["target_category"]
                s_r, e_r = category_row_ranges[h_cat]
                min_p = h["min_percentage"] / 100.0
                # Formula checks if completed items in tests have avg >= 50%
                # IF(SUM(C10:C13)>0, SUM(G10:G13)/SUM(C10:C13) >= 0.5, TRUE)
                hurdle_formulas.append(
                    f'IF(SUM(C{s_r}:C{e_r})>0, IF(SUMIF(E{s_r}:E{e_r}, "<>", C{s_r}:C{e_r})>0, SUM(G{s_r}:G{e_r})/SUMIF(E{s_r}:E{e_r}, "<>", C{s_r}:C{e_r})>={min_p}, TRUE), TRUE)'
                )

        if hurdle_formulas:
            combined_h = f'=IF(AND({", ".join(hurdle_formulas)}), "PASSED", "WARNING: BELOW 50% HURDLE")'
        else:
            combined_h = f'=IF(G5>=0.5, "PASSED", "NEEDS ATTENTION")'
        ws["K5"] = combined_h

        # Style summary cells
        for pos in ["C5", "E5", "G5", "I5", "K5"]:
            ws[pos].fill = CARD_FILL
            ws[pos].border = BOX_BORDER

        # Save metadata for Dashboard cross-referencing
        course_sheet_meta[code] = {
            "title": c["course_name"],
            "credits": c["credits"],
            "is_technical": c["is_technical"],
            "grading_type": c["grading_type"],
            "curr_avg_ref": f"{code}!G5",
            "proj_final_ref": f"{code}!I5",
            "hurdle_ref": f"{code}!K5",
            "completed_weight_ref": f"{code}!C5",
            "earned_weight_ref": f"{code}!E5"
        }
        auto_adjust_column_widths(ws)

    # ==========================================================
    # 2. Create Master "Dashboard & GPA" Tab
    # ==========================================================
    ws_dash = wb.create_sheet(title="Dashboard & GPA", index=0)
    ws_dash.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_dash["A1"] = "Seneca Polytechnic - CTY Semester 3 Grade Dashboard"
    ws_dash["A1"].font = TITLE_FONT
    ws_dash["A2"] = "Automated Academic Performance, Hurdle Monitoring & Seneca 4.0 GPA Calculator"
    ws_dash["A2"].font = SUBTITLE_FONT

    # KPI Summary Cards (Rows 4-6)
    kpis = [
        ("A4", "Cumulative Semester GPA", "A5", "4.0 Scale"),
        ("C4", "Projected Semester GPA", "C5", "Target Estimate"),
        ("E4", "Current Overall Average", "E5", "Weighted Graded"),
        ("G4", "Technical Course Average", "G5", "Major Courses"),
        ("I4", "Total Credits", "I5", "Academic Units")
    ]
    for lbl_cell, label, val_cell, sub in kpis:
        ws_dash[lbl_cell] = label
        ws_dash[lbl_cell].font = Font(name="Calibri", size=9, bold=True, color="64748B")
        ws_dash[val_cell].font = Font(name="Calibri", size=18, bold=True, color="0F172A")
        ws_dash[val_cell].alignment = Alignment(horizontal="center")

    # Table of Courses (Starts at Row 8)
    dash_headers = [
        "Course Code", "Course Name", "Credits", "Course Type",
        "Completed %", "Current Avg %", "Projected Final %", "Letter Grade", "GPA Points", "Hurdle Status"
    ]
    for col_idx, h in enumerate(dash_headers, 1):
        c_cell = ws_dash.cell(row=8, column=col_idx, value=h)
        c_cell.fill = HEADER_FILL
        c_cell.font = HEADER_FONT
        c_cell.alignment = Alignment(horizontal="center", vertical="center")
        c_cell.border = BOX_BORDER

    start_row = 9
    for idx, c in enumerate(courses):
        r = start_row + idx
        code = c["course_code"]
        meta = course_sheet_meta[code]

        ws_dash.cell(row=r, column=1, value=code).font = BOLD_FONT
        ws_dash.cell(row=r, column=2, value=meta["title"]).font = REGULAR_FONT
        
        cr_cell = ws_dash.cell(row=r, column=3, value=meta["credits"])
        cr_cell.font = REGULAR_FONT
        cr_cell.alignment = Alignment(horizontal="right")

        type_str = "Technical Core" if meta["is_technical"] else ("Co-op Prep" if meta["grading_type"] == "sat_un" else "General Ed")
        ws_dash.cell(row=r, column=4, value=type_str).font = REGULAR_FONT

        # Completed % reference
        comp_cell = ws_dash.cell(row=r, column=5, value=f"={meta['completed_weight_ref']}")
        comp_cell.number_format = "0.0%"
        comp_cell.font = REGULAR_FONT
        comp_cell.alignment = Alignment(horizontal="right")

        # Current Avg %
        cur_cell = ws_dash.cell(row=r, column=6, value=f"={meta['curr_avg_ref']}")
        cur_cell.number_format = "0.0%"
        cur_cell.font = BOLD_FONT
        cur_cell.alignment = Alignment(horizontal="right")

        # Projected Final %
        proj_cell = ws_dash.cell(row=r, column=7, value=f"={meta['proj_final_ref']}")
        proj_cell.number_format = "0.0%"
        proj_cell.font = BOLD_FONT
        proj_cell.alignment = Alignment(horizontal="right")

        # Letter Grade (Formula using Seneca Scale: A+ >=90%, A >=80%, B+ >=75%, B >=70%, C+ >=65%, C >=60%, D+ >=55%, D >=50%, F <50%)
        if meta["grading_type"] == "sat_un":
            lg_formula = f'=IF({code}!G5>=0.8, "SAT", "UN")'
            gpa_formula = '"N/A"'
        else:
            lg_formula = (
                f'=IF(G{r}>=0.9, "A+", IF(G{r}>=0.8, "A", IF(G{r}>=0.75, "B+", '
                f'IF(G{r}>=0.7, "B", IF(G{r}>=0.65, "C+", IF(G{r}>=0.6, "C", '
                f'IF(G{r}>=0.55, "D+", IF(G{r}>=0.5, "D", "F"))))))))'
            )
            # Seneca GPA Points: A+/A = 4.0, B+ = 3.5, B = 3.0, C+ = 2.5, C = 2.0, D+ = 1.5, D = 1.0, F = 0.0
            gpa_formula = (
                f'=IF(H{r}="A+", 4.0, IF(H{r}="A", 4.0, IF(H{r}="B+", 3.5, '
                f'IF(H{r}="B", 3.0, IF(H{r}="C+", 2.5, IF(H{r}="C", 2.0, '
                f'IF(H{r}="D+", 1.5, IF(H{r}="D", 1.0, IF(H{r}="F", 0.0, 0.0)))))))))'
            )

        lg_cell = ws_dash.cell(row=r, column=8, value=lg_formula)
        lg_cell.font = BOLD_FONT
        lg_cell.alignment = Alignment(horizontal="center")

        gpa_cell = ws_dash.cell(row=r, column=9, value=gpa_formula)
        gpa_cell.number_format = "0.00"
        gpa_cell.font = BOLD_FONT
        gpa_cell.alignment = Alignment(horizontal="right")

        # Hurdle Status reference
        h_cell = ws_dash.cell(row=r, column=10, value=f"={meta['hurdle_ref']}")
        h_cell.font = BOLD_FONT
        h_cell.alignment = Alignment(horizontal="center")

        for c_i in range(1, 11):
            ws_dash.cell(row=r, column=c_i).border = BOX_BORDER

    end_dash_row = start_row + len(courses) - 1

    # GPA Calculation Formulas (A5, C5)
    # Exclude WTP100 (which has grading_type "sat_un" and GPA "N/A")
    # We sum GPA points * credits for courses row 9 to 14 (CSN305, DAT330, MST300, PSY262, SEC320, OPS345) / 18.0 credits
    graded_rows = [start_row + i for i, c in enumerate(courses) if c["grading_type"] == "percentage_gpa"]
    gpa_products = "+".join([f"(I{r}*C{r})" for r in graded_rows])
    credit_sum = "+".join([f"C{r}" for r in graded_rows])
    ws_dash["A5"] = f"=ROUND(({gpa_products})/({credit_sum}), 2)"
    ws_dash["A5"].number_format = "0.00"

    # Projected GPA
    ws_dash["C5"] = f"=ROUND(({gpa_products})/({credit_sum}), 2)"
    ws_dash["C5"].number_format = "0.00"

    # Current Overall Average % (E5) = Weighted avg of column F
    cur_avg_products = "+".join([f"(F{r}*C{r})" for r in graded_rows])
    ws_dash["E5"] = f"=({cur_avg_products})/({credit_sum})"
    ws_dash["E5"].number_format = "0.0%"

    # Technical Course Average % (G5)
    tech_rows = [start_row + i for i, c in enumerate(courses) if c["is_technical"] and c["grading_type"] == "percentage_gpa"]
    tech_products = "+".join([f"(F{r}*C{r})" for r in tech_rows])
    tech_credit_sum = "+".join([f"C{r}" for r in tech_rows])
    ws_dash["G5"] = f"=({tech_products})/({tech_credit_sum})"
    ws_dash["G5"].number_format = "0.0%"

    # Total Credits (I5)
    ws_dash["I5"] = f"=SUM(C{start_row}:C{end_dash_row})"
    ws_dash["I5"].number_format = "0.0"

    # Seneca GPA Scale Reference Table (Columns L-M)
    ws_dash["L8"] = "Grade"
    ws_dash["L8"].fill = SECTION_FILL
    ws_dash["L8"].font = SECTION_FONT
    ws_dash["M8"] = "GPA"
    ws_dash["M8"].fill = SECTION_FILL
    ws_dash["M8"].font = SECTION_FONT
    scale_rows = [
        ("A+", "4.0", "90% - 100%"),
        ("A",  "4.0", "80% - 89%"),
        ("B+", "3.5", "75% - 79%"),
        ("B",  "3.0", "70% - 74%"),
        ("C+", "2.5", "65% - 69%"),
        ("C",  "2.0", "60% - 64%"),
        ("D+", "1.5", "55% - 59%"),
        ("D",  "1.0", "50% - 54%"),
        ("F",  "0.0", "0% - 49%")
    ]
    for s_i, (lg, pts, pct) in enumerate(scale_rows, 9):
        ws_dash.cell(row=s_i, column=12, value=f"{lg} ({pct})").font = REGULAR_FONT
        ws_dash.cell(row=s_i, column=12).border = BOX_BORDER
        p_c = ws_dash.cell(row=s_i, column=13, value=float(pts))
        p_c.font = BOLD_FONT
        p_c.number_format = "0.0"
        p_c.border = BOX_BORDER

    auto_adjust_column_widths(ws_dash)

    # ==========================================================
    # 3. Create "What-If Simulator" Tab
    # ==========================================================
    ws_whatif = wb.create_sheet(title="What-If Simulator")
    ws_whatif.views.sheetView[0].showGridLines = True

    ws_whatif["A1"] = "What-If Final Grade Simulator & Target Solver"
    ws_whatif["A1"].font = TITLE_FONT
    ws_whatif["A2"] = "Calculate required score on unsubmitted deliverables to achieve target letter grade"
    ws_whatif["A2"].font = SUBTITLE_FONT

    wi_headers = [
        "Course Code", "Course Name", "Credits", "Completed Weight %",
        "Earned Weight %", "Current Avg %", "Target Grade", "Target %",
        "Remaining Weight %", "Required Avg on Remaining %", "Feasibility"
    ]
    for col_idx, h in enumerate(wi_headers, 1):
        c_cell = ws_whatif.cell(row=4, column=col_idx, value=h)
        c_cell.fill = HEADER_FILL
        c_cell.font = HEADER_FONT
        c_cell.alignment = Alignment(horizontal="center", vertical="center")
        c_cell.border = BOX_BORDER

    for idx, c in enumerate([c for c in courses if c["grading_type"] == "percentage_gpa"]):
        r = 5 + idx
        code = c["course_code"]
        ws_whatif.cell(row=r, column=1, value=code).font = BOLD_FONT
        ws_whatif.cell(row=r, column=2, value=c["course_name"]).font = REGULAR_FONT
        ws_whatif.cell(row=r, column=3, value=c["credits"]).font = REGULAR_FONT

        # Completed Weight =CSN305!C5
        cw = ws_whatif.cell(row=r, column=4, value=f"={code}!C5")
        cw.number_format = "0.0%"
        cw.font = REGULAR_FONT

        # Earned Weight =CSN305!E5
        ew = ws_whatif.cell(row=r, column=5, value=f"={code}!E5")
        ew.number_format = "0.00%"
        ew.font = REGULAR_FONT

        # Current Avg =CSN305!G5
        ca = ws_whatif.cell(row=r, column=6, value=f"={code}!G5")
        ca.number_format = "0.0%"
        ca.font = BOLD_FONT

        # Target Grade (Default: A = 80%)
        ws_whatif.cell(row=r, column=7, value="A").font = BOLD_FONT
        ws_whatif.cell(row=r, column=7).alignment = Alignment(horizontal="center")

        # Target % formula based on column G
        tp_formula = (
            f'=IF(G{r}="A+", 0.90, IF(G{r}="A", 0.80, IF(G{r}="B+", 0.75, '
            f'IF(G{r}="B", 0.70, IF(G{r}="C+", 0.65, IF(G{r}="C", 0.60, '
            f'IF(G{r}="D+", 0.55, IF(G{r}="D", 0.50, 0.50))))))))'
        )
        tp = ws_whatif.cell(row=r, column=8, value=tp_formula)
        tp.number_format = "0.0%"
        tp.font = REGULAR_FONT

        # Remaining Weight % = 1.0 - Completed Weight (D{r})
        rw = ws_whatif.cell(row=r, column=9, value=f"=1.0-D{r}")
        rw.number_format = "0.0%"
        rw.font = REGULAR_FONT

        # Required Avg on Remaining = (Target % - Earned Weight %) / Remaining Weight %
        # Formula: =IF(I{r}>0, (H{r}-E{r})/I{r}, "Finished")
        req_formula = f'=IF(I{r}>0, (H{r}-E{r})/I{r}, "Finished")'
        req = ws_whatif.cell(row=r, column=10, value=req_formula)
        req.number_format = "0.0%"
        req.font = BOLD_FONT

        # Feasibility check
        feas_formula = f'=IF(I{r}<=0, "Completed", IF(J{r}>1.0, "Impossible (>100%)", IF(J{r}<=0, "Secured", IF(J{r}>=0.85, "Challenging", "Achievable"))))'
        feas = ws_whatif.cell(row=r, column=11, value=feas_formula)
        feas.font = BOLD_FONT
        feas.alignment = Alignment(horizontal="center")

        for col_i in range(1, 12):
            ws_whatif.cell(row=r, column=col_i).border = BOX_BORDER

    auto_adjust_column_widths(ws_whatif)

    # ==========================================================
    # 4. Create "Timeline & Milestones" Tab
    # ==========================================================
    ws_time = wb.create_sheet(title="Timeline & Milestones")
    ws_time.views.sheetView[0].showGridLines = True

    ws_time["A1"] = "Semester 3 Deliverables Timeline & Tracking"
    ws_time["A1"].font = TITLE_FONT
    ws_time["A2"] = "Chronological view of all course assignments, weights, and completion status"
    ws_time["A2"].font = SUBTITLE_FONT

    time_headers = ["Course", "Assessment Item", "Category", "Weight %", "Due Date", "Status"]
    for col_idx, h in enumerate(time_headers, 1):
        c_cell = ws_time.cell(row=4, column=col_idx, value=h)
        c_cell.fill = HEADER_FILL
        c_cell.font = HEADER_FONT
        c_cell.alignment = Alignment(horizontal="center", vertical="center")
        c_cell.border = BOX_BORDER

    # Collect all items across all courses
    all_timeline_items = []
    for c in courses:
        code = c["course_code"]
        for cat in c["categories"]:
            for item in cat["items"]:
                all_timeline_items.append({
                    "course": code,
                    "name": item["name"],
                    "category": cat["name"],
                    "weight": item["weight_percent"],
                    "due_date": item.get("due_date") or "TBA",
                    "status": item.get("status") or "Not Started"
                })

    # Sort items by due date (TBA at bottom)
    def date_sort_key(it):
        d = it["due_date"]
        if not d or d == "TBA":
            return "9999-99-99"
        parts = d.split("-")
        if len(parts) == 3:
            return f"{parts[0]:0>4}-{int(parts[1]):0>2}-{int(parts[2]):0>2}"
        return d

    all_timeline_items.sort(key=date_sort_key)

    for idx, item in enumerate(all_timeline_items):
        r = 5 + idx
        ws_time.cell(row=r, column=1, value=item["course"]).font = BOLD_FONT
        ws_time.cell(row=r, column=2, value=item["name"]).font = REGULAR_FONT
        ws_time.cell(row=r, column=3, value=item["category"]).font = REGULAR_FONT
        
        w_c = ws_time.cell(row=r, column=4, value=item["weight"] / 100.0)
        w_c.number_format = "0.0%"
        w_c.font = REGULAR_FONT
        w_c.alignment = Alignment(horizontal="right")

        ws_time.cell(row=r, column=5, value=item["due_date"]).font = REGULAR_FONT
        ws_time.cell(row=r, column=5).alignment = Alignment(horizontal="center")

        st_c = ws_time.cell(row=r, column=6, value=item["status"])
        st_c.font = BOLD_FONT
        st_c.alignment = Alignment(horizontal="center")
        if item["status"] == "Done":
            st_c.fill = SUCCESS_FILL
            st_c.font = SUCCESS_FONT
        elif item["status"] == "In Progress":
            st_c.fill = CARD_FILL

        for col_i in range(1, 7):
            ws_time.cell(row=r, column=col_i).border = BOX_BORDER

    auto_adjust_column_widths(ws_time)

    # Save Workbook
    wb.save(output_file)
    print(f"[✓] Successfully generated '{output_file}' with {len(wb.sheetnames)} tabs:")
    for s in wb.sheetnames:
        print(f"    - {s}")

if __name__ == "__main__":
    generate_workbook()

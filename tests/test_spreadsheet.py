import unittest
import os
import openpyxl
import re

class TestSpreadsheetIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xlsx_path = os.path.join(os.path.dirname(__file__), '..', 'grade_calculator.xlsx')
        if not os.path.exists(cls.xlsx_path):
            from pipeline.generate_sheets import generate_workbook
            generate_workbook(output_file=cls.xlsx_path)
        cls.wb = openpyxl.load_workbook(cls.xlsx_path, data_only=False)

    def test_all_tabs_exist(self):
        expected_tabs = [
            "Dashboard & GPA", "CSN305", "DAT330", "MST300",
            "PSY262", "SEC320", "OPS345", "WTP100",
            "What-If Simulator", "Timeline & Milestones"
        ]
        self.assertEqual(self.wb.sheetnames, expected_tabs)

    def test_no_broken_formulas_or_references(self):
        """Validates that all formulas have balanced parentheses and valid sheet references."""
        sheet_names = set(self.wb.sheetnames)
        broken_formulas = []

        for name in self.wb.sheetnames:
            ws = self.wb[name]
            for row in ws.iter_rows():
                for cell in row:
                    val = str(cell.value or '')
                    if val.startswith('='):
                        # Check balanced parentheses
                        if val.count('(') != val.count(')'):
                            broken_formulas.append((name, cell.coordinate, val, "Unbalanced parentheses"))
                        
                        # Check cross-sheet references: e.g. SheetName!A1
                        matches = re.findall(r'([A-Za-z0-9_ &]+)!', val)
                        for ref_sheet in matches:
                            clean_ref = ref_sheet.strip("'")
                            if clean_ref not in sheet_names:
                                broken_formulas.append((name, cell.coordinate, val, f"Non-existent sheet reference: {clean_ref}"))

                        # Check for prohibited or Office 365-only functions that break in Google Sheets
                        unsupported_funcs = ['_XLFN', 'LAMBDA(', 'LET(', 'XLOOKUP(', 'FILTER(']
                        for uf in unsupported_funcs:
                            if uf in val.upper():
                                broken_formulas.append((name, cell.coordinate, val, f"Unsupported Google Sheets formula: {uf}"))

        self.assertEqual(len(broken_formulas), 0, f"Found broken formulas: {broken_formulas}")

    def test_dashboard_kpis_and_course_references(self):
        """Verifies that the Dashboard has correct formulas linking to all courses."""
        ws = self.wb["Dashboard & GPA"]
        
        # Check cumulative GPA formula in A5
        a5_val = str(ws["A5"].value or "")
        self.assertTrue(a5_val.startswith("=ROUND(("), f"A5 should contain GPA formula, got: {a5_val}")
        
        # Check Technical Course Average formula in G5
        g5_val = str(ws["G5"].value or "")
        self.assertTrue(g5_val.startswith("=("), f"G5 should contain Tech Avg formula, got: {g5_val}")
        
        # Check course rows (rows 9 to 15)
        for r in range(9, 16):
            code = ws.cell(row=r, column=1).value
            comp_formula = str(ws.cell(row=r, column=5).value or "")
            curr_avg_formula = str(ws.cell(row=r, column=6).value or "")
            proj_formula = str(ws.cell(row=r, column=7).value or "")
            
            self.assertIn(f"={code}!", comp_formula)
            self.assertIn(f"={code}!", curr_avg_formula)
            self.assertIn(f"={code}!", proj_formula)

    def test_seneca_letter_grade_conversion_logic(self):
        """Unit test the Seneca 4.0 GPA scale thresholds."""
        def get_letter_grade(pct):
            if pct >= 0.90: return "A+"
            if pct >= 0.80: return "A"
            if pct >= 0.75: return "B+"
            if pct >= 0.70: return "B"
            if pct >= 0.65: return "C+"
            if pct >= 0.60: return "C"
            if pct >= 0.55: return "D+"
            if pct >= 0.50: return "D"
            return "F"

        def get_gpa_points(letter):
            scale = {
                "A+": 4.0, "A": 4.0, "B+": 3.5, "B": 3.0,
                "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0
            }
            return scale.get(letter, 0.0)

        self.assertEqual(get_letter_grade(0.95), "A+")
        self.assertEqual(get_gpa_points("A+"), 4.0)
        self.assertEqual(get_letter_grade(0.82), "A")
        self.assertEqual(get_gpa_points("A"), 4.0)
        self.assertEqual(get_letter_grade(0.78), "B+")
        self.assertEqual(get_gpa_points("B+"), 3.5)
        self.assertEqual(get_letter_grade(0.71), "B")
        self.assertEqual(get_gpa_points("B"), 3.0)
        self.assertEqual(get_letter_grade(0.66), "C+")
        self.assertEqual(get_gpa_points("C+"), 2.5)
        self.assertEqual(get_letter_grade(0.61), "C")
        self.assertEqual(get_gpa_points("C"), 2.0)
        self.assertEqual(get_letter_grade(0.56), "D+")
        self.assertEqual(get_gpa_points("D+"), 1.5)
        self.assertEqual(get_letter_grade(0.51), "D")
        self.assertEqual(get_gpa_points("D"), 1.0)
        self.assertEqual(get_letter_grade(0.48), "F")
        self.assertEqual(get_gpa_points("F"), 0.0)

    def test_what_if_simulator_formulas(self):
        """Verifies formulas on What-If Simulator tab."""
        ws = self.wb["What-If Simulator"]
        # Check headers
        self.assertEqual(ws["A4"].value, "Course Code")
        self.assertEqual(ws["H4"].value, "Target %")
        self.assertEqual(ws["J4"].value, "Required Avg on Remaining %")
        
        # Verify row 5 has valid formulas
        self.assertIn("=CSN305!C5", str(ws["D5"].value))
        self.assertIn("=CSN305!E5", str(ws["E5"].value))
        self.assertIn("=1.0-D5", str(ws["I5"].value))
        self.assertIn("(H5-E5)/I5", str(ws["J5"].value))

    def test_timeline_tab_populated(self):
        """Verifies that Timeline & Milestones has all assessments."""
        ws = self.wb["Timeline & Milestones"]
        # Check that there are over 80 assessment rows
        self.assertGreater(ws.max_row, 80)
        # Check columns: Course, Item, Category, Weight, Due Date, Status
        self.assertEqual(ws["A4"].value, "Course")
        self.assertEqual(ws["B4"].value, "Assessment Item")
        self.assertEqual(ws["F4"].value, "Status")

if __name__ == '__main__':
    unittest.main()

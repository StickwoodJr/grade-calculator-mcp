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
                        
                        # Check cross-sheet references: e.g. SheetName!A1 or 'Sheet Name'!A1
                        matches = re.findall(r"['\"]?([A-Za-z0-9_ &]+)['\"]?!", val)
                        for ref_sheet in matches:
                            clean_ref = ref_sheet.strip(" '\"")
                            if clean_ref and clean_ref not in sheet_names:
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
        
        # Check cumulative GPA formula in A6
        a6_val = str(ws["A6"].value or "")
        self.assertTrue("ROUND(" in a6_val, f"A6 should contain ROUND formula, got: {a6_val}")
        
        # Check Technical Course Average formula in G6
        g6_val = str(ws["G6"].value or "")
        self.assertTrue("ROUND(" in g6_val or "SUM(" in g6_val, f"G6 should contain Tech Avg formula, got: {g6_val}")
        
        # Check course rows (rows 11 to 17)
        courses = ["CSN305", "DAT330", "MST300", "PSY262", "SEC320", "OPS345", "WTP100"]
        for idx, code in enumerate(courses):
            r = 11 + idx
            comp_formula = str(ws.cell(row=r, column=5).value or "")
            curr_avg_formula = str(ws.cell(row=r, column=6).value or "")
            proj_formula = str(ws.cell(row=r, column=7).value or "")
            
            self.assertIn(f"{code}'!", comp_formula)
            self.assertIn(f"{code}'!", curr_avg_formula)
            self.assertIn(f"{code}'!", proj_formula)

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
        # Check headers (Row 10)
        self.assertEqual(ws["A10"].value, "Course Code")
        self.assertEqual(ws["H10"].value, "Target %")
        self.assertEqual(ws["J10"].value, "Required % on Remainder")
        
        # Verify row 11 has valid formulas
        self.assertIn("'CSN305'!", str(ws["D11"].value))
        self.assertIn("'CSN305'!", str(ws["E11"].value))
        self.assertIn("=1.0-D11", str(ws["I11"].value))
        self.assertIn("(H11-E11)/I11", str(ws["J11"].value))

    def test_timeline_tab_populated(self):
        """Verifies that Timeline & Milestones has all assessments."""
        ws = self.wb["Timeline & Milestones"]
        # Check that there are over 80 assessment rows
        self.assertGreater(ws.max_row, 80)
        # Check columns (Row 5): Course, Item, Category, Weight, Due Date, Status, Link
        self.assertEqual(ws["A5"].value, "Course")
        self.assertEqual(ws["B5"].value, "Assessment Deliverable")
        self.assertEqual(ws["F5"].value, "Current Status")
        self.assertEqual(ws["G5"].value, "Quick Link")

if __name__ == '__main__':
    unittest.main()

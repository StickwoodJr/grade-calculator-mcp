# Seneca CTY Grade Calculator & ExtendLM MCP Ingestion Pipeline

[![Tests](https://img.shields.io/badge/tests-16%20passed-success)](tests/)
[![Vite](https://img.shields.io/badge/vite-5.4.11-646CFF)](https://vitejs.dev/)
[![React](https://img.shields.io/badge/react-18.3.1-61DAFB)](https://react.dev/)
[![Spreadsheet](https://img.shields.io/badge/excel-compatible-217346)](grade_calculator.xlsx)
[![Seneca 4.0](https://img.shields.io/badge/gpa-Seneca%204.0%20Scale-red)](https://www.senecapolytechnic.ca/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end academic performance tracking system and agentic syllabus ingestion pipeline built for **Seneca Polytechnic Computer Systems Technology (CTY) Semester 3**. 

This project integrates with **ExtendLM's MCP server** to query **Gemini Notebook (NotebookLM)** for class syllabus analysis, extracts structured course grading schemas via a class-isolated 5-pass prompt sequence, and outputs both:
1. **Automated Multi-Tab `.xlsx` Workbook** with dynamic Excel/Google Sheets formulas, dual-criterion passing hurdle checks, and Seneca 4.0 GPA lookup tables.
2. **Interactive Web Spreadsheet Dashboard** (React, TypeScript, Tailwind CSS, SheetJS) with real-time recalculation, What-If target solvers, and GitHub Pages deployment.

---

## Architecture Overview

```
                          [Syllabus PDFs]
                                 │
                                 ▼
                     [ExtendLM MCP Server]
                  (https://mcp.extendlm.com/mcp)
                                 │
                                 ▼
                    [Gemini Notebook / NotebookLM]
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
         [Pass 1: Course Identity]    [Pass 2: Category Weights (100%)]
         [Pass 3: Itemized Deliverables] [Pass 4: Passing Hurdles]
                    └────────────┬────────────┘
                                 │
                                 ▼
                    [data/courses/*.json Schemas]
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
   [pipeline/generate_sheets.py]           [web/ (React + Vite)]
              ▼                                     ▼
    [grade_calculator.xlsx]              [GitHub Pages Web App]
   (Excel & Google Sheets)              (Live Editable Data-Grid)
```

---

## Features

- **Class-Isolated Multi-Pass Syllabus Extraction**: 5-pass extraction sequence targeting Identity, Category Weights, Itemized Assessments, Hurdles, and Policies, with strict source-pinning in MCP queries.
- **Dual Deliverable Formats**:
  - **Excel `.xlsx` Workbook**: 10 tabs (`Dashboard & GPA`, 7 course tabs, `What-If Simulator`, `Timeline & Milestones`), styled with freeze panes, borders, and universal formulas compatible with Microsoft Excel and Google Sheets.
  - **Modern Web Application**: Interactive editable data grid, Seneca GPA meter, hurdle alerts, and client-side Excel export.
- **Dual-Criterion Passing Hurdle Detection**: Seneca technology courses often mandate passing sub-averages (e.g. $\ge 50\%$ on all tests combined). The calculator automatically evaluates test/lab sub-averages and displays visual alerts if a student is in jeopardy of failing a hurdle.
- **Technical Major Average vs. Overall GPA**: Automatically isolates major computing courses (`CSN305`, `DAT330`, `MST300`, `OPS345`, `SEC320`) from general electives (`PSY262`) and SAT/UN courses (`WTP100`).
- **Target Grade & What-If Solver**: Interactive simulation calculating the exact percentage required on remaining deliverables to achieve a target letter grade (A+, A, B+, B, C+, C, D).
- **Offline & MCP Fallbacks**: Includes verified pre-populated JSON configurations for all 7 Seneca CTY Semester 3 courses with 110+ itemized assignments synchronized with the semester calendar.

---

## Course Roster (Seneca CTY Semester 3)

| Course Code | Course Name | Credits | Type | Evaluation Breakdown | Passing Hurdle |
|:---|:---|:---:|:---:|:---|:---|
| **CSN305** | Virtualization and Cloud Infrastructure | 3.0 | Tech Core | Labs (10 @ 4% = 40%), Tests (4 @ 15% = 60%) | $\ge 50\%$ Test Avg, All Labs Completed |
| **DAT330** | Introduction to Databases | 3.0 | Tech Core | Labs (20%), Quizzes (10%), Assignments (15%), Midterm (15%), Final Test (15%), Project (15%), Budget (10%) | $\ge 50\%$ Labs, $\ge 50\%$ Tests, $\ge 50\%$ Asg/Proj |
| **MST300** | Intro to Microsoft Cloud Technologies | 3.0 | Tech Core | Labs (20%), Quizzes (15%), Projects (30%), Tests (25%), Budget (10%) | $\ge 50\%$ Labs, $\ge 50\%$ Projects |
| **PSY262** | Applied Psychology of Mindfulness | 3.0 | Gen Ed | In-Class (25%), Writing (10%), Quiz 1 (20%), Quiz 2 (20%), Final Exam (25%) | $\ge 50\%$ Overall |
| **SEC320** | Incident Response & Computer Forensics | 3.0 | Tech Core | Practical Tests (30%), Labs (40%), Final Project (30%) | $\ge 50\%$ Tests, $\ge 50\%$ Labs, All Labs Done |
| **OPS345** | Open System Application Server | 3.0 | Tech Core | Labs (16%), Assignments (30%), Quizzes (4%), Midterm (25%), Final Test (25%) | $\ge 50\%$ Overall |
| **WTP100** | Work Term Preparation | 1.0 | Co-op Prep | 14 Modules / Knowledge Checks (100%) | $\ge 80\%$ on all 14 Knowledge Checks (SAT/UN) |

---

## Seneca Official GPA Scale (4.0)

| Grade | Range | GPA Points |
|:---:|:---:|:---:|
| **A+** | 90% – 100% | 4.0 |
| **A** | 80% – 89% | 4.0 |
| **B+** | 75% – 79% | 3.5 |
| **B** | 70% – 74% | 3.0 |
| **C+** | 65% – 69% | 2.5 |
| **C** | 60% – 64% | 2.0 |
| **D+** | 55% – 59% | 1.5 |
| **D** | 50% – 54% | 1.0 |
| **F** | 0% – 49% | 0.0 |
| **SAT / UN** | Satisfactory / Unsatisfactory | Excluded from numerical GPA |

---

## Quickstart

### 1. Generate Spreadsheet (`grade_calculator.xlsx`)
```bash
# Install Python dependencies
pip install openpyxl jsonschema

# Compile the multi-tab Excel workbook
python3 pipeline/generate_sheets.py
```
The output file `grade_calculator.xlsx` can be opened in Microsoft Excel, LibreOffice Calc, or imported into Google Sheets via **File $\rightarrow$ Import $\rightarrow$ Upload**.

### 2. Launch Web Dashboard Locally
```bash
cd web
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Run Automated Verification Tests
```bash
# Run Python spreadsheet and schema test suites
python3 -m unittest discover tests/

# Run Web calculation engine unit tests
npm test --prefix web
```

---

## Using ExtendLM MCP with AI Assistants

This project includes an AI skill (`skills/extendlm-grade-extractor/SKILL.md`) for Antigravity, Claude Code, Cursor, and Codex.

### Connecting Claude Code:
```bash
claude mcp add --transport http extendlm --scope user https://mcp.extendlm.com/mcp
claude mcp login extendlm
```

### Running the Extraction CLI:
```bash
# Verify existing course schemas
python3 pipeline/extract.py --verify

# Run offline extraction from syllabus PDFs
python3 pipeline/extract.py --mode local --source-dir "/path/to/syllabi"

# Run remote MCP extraction via ExtendLM and NotebookLM
python3 pipeline/extract.py --mode mcp --notebook-id "<notebook-id>"
```

---

## Contributing

Pull requests are welcome! Please ensure all test suites pass before opening PRs:
```bash
python3 -m unittest discover tests/ && npm test --prefix web && npm run build --prefix web
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

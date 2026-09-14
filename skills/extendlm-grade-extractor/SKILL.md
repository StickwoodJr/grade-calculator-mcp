---
name: extendlm-grade-extractor
description: Extracts course grading breakdowns, passing hurdles, and assessment schedules from syllabi using ExtendLM MCP and Gemini Notebook (NotebookLM).
---

# ExtendLM MCP Syllabus Grade Extractor Skill

This skill guides AI coding assistants (Antigravity, Claude Code, Cursor, Codex) in extracting course grading policies from syllabi using **ExtendLM**'s Model Context Protocol (MCP) server connected to **Gemini Notebook (NotebookLM)**.

## Architecture

ExtendLM exposes Gemini Notebook through a remote MCP server at `https://mcp.extendlm.com/mcp`. The connection bridges directly to the user's active Chrome browser session where the ExtendLM extension is authenticated.

```
[Local Syllabus PDFs] -> [ExtendLM MCP: prepare_pdf_source_upload / add_pdf_source] -> [Gemini Notebook]
                                                                                              |
                                                          [ask_notebook: 5-Pass Isolated Extraction]
                                                                                              |
                                                                                  [data/courses/*.json]
                                                                                              |
                                                    [pipeline/generate_sheets.py] -> [grade_calculator.xlsx]
                                                    [web/ (Vite + React)]        -> [GitHub Pages Dashboard]
```

## Connecting ExtendLM MCP to Your AI Assistant

### 1. Claude Code
```bash
claude mcp add --transport http extendlm --scope user https://mcp.extendlm.com/mcp
claude mcp login extendlm
```

### 2. Antigravity IDE
Add the following entry to your MCP configuration (`mcp_config.json`):
```json
{
  "mcpServers": {
    "extendlm": {
      "url": "https://mcp.extendlm.com/mcp",
      "transport": "sse"
    }
  }
}
```

### 3. Cursor
In Cursor Settings $\rightarrow$ Features $\rightarrow$ MCP $\rightarrow$ Add New MCP Server:
- Name: `extendlm`
- Type: `SSE`
- URL: `https://mcp.extendlm.com/mcp`

---

## The 5-Pass Class-Isolated Extraction Sequence

To eliminate hallucinations and prevent cross-course bleed-through when multiple syllabi reside in a notebook, execute 5 isolated passes per course with source-binding:

### Pass 1: Course Identity & Scope
> **Prompt**: `Focus EXCLUSIVELY on course '{CODE}' from document '{DOC}'. What is the Course Code, Course Title, Credit Value, Academic Term, and whether this is a technical computing course or general elective? Identify if grading is standard percentage GPA or SAT/UN (pass/fail). Respond strictly in JSON: {"course_code": "...", "course_name": "...", "credits": 3.0, "is_technical": true/false, "grading_type": "percentage_gpa"|"sat_un"}`

### Pass 2: High-Level Evaluation Categories (100% Total)
> **Prompt**: `Focus EXCLUSIVELY on course '{CODE}'. List every top-level assessment category (e.g. Labs, Quizzes, Assignments, Midterm, Final Exam, Project, Budget) and its exact percentage weight. The total sum of weights MUST equal 100%. Respond in JSON: {"categories": [{"name": "...", "weight_percent": 40.0}, ...]}`

### Pass 3: Granular Assessment Items & Weights
> **Prompt**: `Focus EXCLUSIVELY on course '{CODE}'. List every individual lab, quiz, test, and assignment with its specific weight percentage, maximum points, and scheduled due date (if present). Respond in JSON: {"items": [{"category": "...", "name": "Lab 1", "weight_percent": 4.0, "max_points": 100, "due_date": "YYYY-MM-DD"|null}, ...]}`

### Pass 4: Passing Criteria & Hurdle Policies
> **Prompt**: `Focus EXCLUSIVELY on course '{CODE}'. Are there specific passing hurdles required to earn credit? (e.g., must achieve >= 50% weighted average on tests, >= 50% on labs, or mandatory submission requirements). Respond in JSON: {"passing_criteria": ["..."], "hurdles": [{"type": "category_average", "target_category": "tests", "min_percentage": 50.0, "description": "..."}]}`

### Pass 5: Exceptions, Drop Lowest & Special Scales
> **Prompt**: `Focus EXCLUSIVELY on course '{CODE}'. Are there any 'drop lowest score' rules, late penalty rules, or non-standard grade scales? Respond in JSON: {"drop_rules": [{"category": "...", "drop_lowest_n": 1}], "grade_scale": "Seneca 4.0"}`

---

## Verification & Compilation Commands

After extracting course configs:
```bash
# 1. Validate schemas
python3 pipeline/extract.py --verify
python3 -m unittest tests/test_schemas.py

# 2. Re-generate spreadsheet
python3 pipeline/generate_sheets.py
python3 -m unittest tests/test_spreadsheet.py

# 3. Build web dashboard
npm test --prefix web
npm run build --prefix web
```

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
                                                                                              │
                                                       [ask_notebook: 5-Pass Production LLM Prompts]
                                                                                              │
                                                                                  [data/courses/*.json]
                                                                                              │
                                                    [pipeline/generate_sheets.py] -> [grade_calculator.xlsx]
                                                    [web/ (Vite + React)]        -> [GitHub Pages Dashboard]
```

## Connecting ExtendLM MCP to Your AI Assistant

### 1. Claude Code
Run:
```bash
claude mcp add --transport http extendlm --scope user https://mcp.extendlm.com/mcp
claude mcp login extendlm
```
Complete OAuth approval in your browser.

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

---

## Production-Grade 5-Pass Gemini Notebook LLM Prompts

NotebookLM uses Gemini 1.5 Pro with full document context and source grounding. Each pass below uses academic role framing, strict grounding constraints, footnote scanning, and rigorous JSON output schemas:

### Pass 1: Course Identity, Academic Scope & Grading Scale
```markdown
### ROLE & OBJECTIVE
You are an expert Academic Registrar and Curriculum Analyst. Your task is to analyze the course syllabus for **{COURSE_CODE}** from document '{SOURCE_FILE}' and extract its core identity, academic classification, and grading system.

### EXTRACTION DIRECTIVES
1. Source Grounding: Focus EXCLUSIVELY on the course outline and header information for '{COURSE_CODE}'. Cite the document title and page number.
2. Course Classification:
   - Classify as `is_technical: true` if the subject involves practical computing skills (cloud infrastructure, virtualization, databases, incident response, operating systems, Linux, networking, programming).
   - Classify as `is_technical: false` if it is a General Education elective (psychology, philosophy, humanities) or Co-op/Career preparation.
3. Grading System:
   - Set `grading_type: "sat_un"` if the course is evaluated on a binary Satisfactory / Unsatisfactory basis without numerical GPA.
   - Set `grading_type: "percentage_gpa"` if standard letter grades and GPA points are awarded based on weighted percentages.

### OUTPUT SPECIFICATION (Raw JSON only)
{
  "course_code": "{COURSE_CODE}",
  "course_name": "Full Official Course Title",
  "credits": 3.0,
  "term": "Academic Term (e.g. Fall 2026)",
  "is_technical": true,
  "grading_type": "percentage_gpa",
  "grade_scale": "Seneca 4.0",
  "citation": "Document Title, Page X"
}
```

### Pass 2: High-Level Evaluation Categories (100% Total)
```markdown
### ROLE & OBJECTIVE
You are an Academic Auditor verifying syllabus compliance and grading scheme integrity for **{COURSE_CODE}**.

### EXTRACTION DIRECTIVES
1. Locate the "Modes of Evaluation" or "Evaluation Scheme" table.
2. Identify every top-level assessment category (e.g., Labs, Practical Tests, Quizzes, Assignments, Midterm Exam, Final Exam, Projects, Management of Budget Allotment).
3. Extract the exact percentage weight assigned to each category.
4. CRITICAL INTEGRITY CHECK: The sum of all category weights MUST equal exactly 100.0%.

### OUTPUT SPECIFICATION (Raw JSON only)
{
  "course_code": "{COURSE_CODE}",
  "total_weight_verified": 100.0,
  "categories": [
    {
      "category_id": "unique_lowercase_id (e.g. labs, tests, quizzes)",
      "name": "Official Category Name",
      "weight_percent": 40.0,
      "description": "Short description of what this category evaluates",
      "citation": "Page X, Section Y"
    }
  ]
}
```

### Pass 3: Granular Assessment Items & Weekly Schedule
```markdown
### ROLE & OBJECTIVE
You are an Academic Operations Specialist creating a granular assessment tracker for **{COURSE_CODE}**.

### EXTRACTION DIRECTIVES
1. Cross-reference the "Modes of Evaluation" table with the "Tentative Weekly Schedule" and assignment lists.
2. Enumerate EVERY individual deliverable that contributes to the final grade:
   - Every individual lab (Lab 1 through Lab 10)
   - Every individual quiz (Quiz 1 through Quiz 5)
   - Every individual assignment, midterm test, practical test, final test, and project milestone.
3. For each deliverable, specify: item name, category ID, weight percentage, max points (default 100), and scheduled due date / week.

### OUTPUT SPECIFICATION (Raw JSON only)
{
  "course_code": "{COURSE_CODE}",
  "total_items_count": 14,
  "items": [
    {
      "id": "{course_code.lower()}-lab-1",
      "category_id": "labs",
      "name": "Lab 1",
      "weight_percent": 4.0,
      "max_points": 100,
      "due_date": "2026-09-17",
      "scheduled_week": "Week 2",
      "citation": "Page X, Weekly Schedule"
    }
  ]
}
```

### Pass 4: Passing Hurdles & Dual-Criterion Policies
```markdown
### ROLE & OBJECTIVE
You are an Academic Standards and Appeals Officer auditing critical passing criteria and dual-criterion hurdles for **{COURSE_CODE}**.

### EXTRACTION DIRECTIVES
1. Carefully inspect the "Note", "Student Progression and Promotion Policy", "To obtain a credit in this course", or asterisked footnotes beneath the evaluation table.
2. Identify all Dual-Criterion Passing Hurdles where a student can FAIL the course despite having an overall passing mark:
   - Mandatory test/exam sub-minimum (e.g., "Achieve a weighted average of >= 50% on all tests combined").
   - Mandatory lab sub-minimum (e.g., "Achieve a weighted average of >= 50% on all labs").
   - Mandatory project completion or submission of all deliverables.
   - For SAT/UN: minimum passing score per module (e.g. >= 80% on each knowledge check).
3. Detail the exact consequences if a hurdle is not met.

### OUTPUT SPECIFICATION (Raw JSON only)
{
  "course_code": "{COURSE_CODE}",
  "has_hurdles": true,
  "passing_criteria": [
    "Achieve an overall course grade of 50% or higher",
    "Achieve a weighted average of 50% or higher on all tests"
  ],
  "hurdles": [
    {
      "type": "category_average",
      "target_category": "tests",
      "min_percentage": 50.0,
      "consequence": "Failure of course regardless of lab/assignment grades",
      "description": "Achieve a weighted average of 50% or higher on all tests",
      "citation": "Page X, Note 2"
    }
  ]
}
```

### Pass 5: Exceptions, Drop Policies & Grade Scale
```markdown
### ROLE & OBJECTIVE
You are an Academic Policy Consultant analyzing accommodations, exception handling, and drop policies for **{COURSE_CODE}**.

### EXTRACTION DIRECTIVES
1. Search for "Drop Lowest Score" policies (e.g., 'best 8 of 10 labs counted').
2. Search for Late Submission Penalties (e.g. 10% per day).
3. Search for Missed Test & Assessment Policies.
4. Search for Reference Sheets / Exam Aids allowed.

### OUTPUT SPECIFICATION (Raw JSON only)
{
  "course_code": "{COURSE_CODE}",
  "drop_policies": [
    {
      "category": "quizzes",
      "drop_lowest_n": 1,
      "description": "Lowest quiz score is dropped from calculation"
    }
  ],
  "late_penalty_policy": "Description or null",
  "exam_aids_allowed": "Description or null",
  "grade_scale": "Seneca 4.0",
  "citation": "Page X"
}
```

---

## Live Execution Pipeline

```bash
# Run end-to-end NotebookLM live orchestrator
python3 pipeline/run_agent_notebook.py
```

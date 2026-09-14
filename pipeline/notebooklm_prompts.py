"""
Production-Grade Gemini Notebook (NotebookLM) LLM Extraction Prompts.

Engineered specifically for Gemini 1.5 Pro/Flash in NotebookLM with:
- Deep academic registrar role framing
- Strict source-grounding directives (citations required)
- Multi-page table and footnote scanning
- Dual-criterion passing hurdle extraction
- Precise JSON output schemas
"""

def get_pass_1_identity_prompt(course_code: str, source_filename: str = "") -> str:
    source_constraint = f" from the uploaded document '{source_filename}'" if source_filename else ""
    return f"""### ROLE & OBJECTIVE
You are an expert Academic Registrar and Curriculum Analyst at an accredited technical college.
Your task is to analyze the course syllabus{source_constraint} for **{course_code}** and extract its core identity, academic classification, and grading system.

### EXTRACTION DIRECTIVES
1. **Source Grounding**: Focus EXCLUSIVELY on the course outline and header information for '{course_code}'. Cite the document title and page number.
2. **Course Classification**:
   - Classify as `is_technical: true` if the subject matter involves technical computing core skills (e.g. cloud infrastructure, virtualization, databases, incident response, operating systems, Linux/Unix, network administration, software development).
   - Classify as `is_technical: false` if it is a General Education elective (e.g., psychology, philosophy, humanities) or Co-op/Career preparation.
3. **Grading System**:
   - Set `grading_type: "sat_un"` if the course is evaluated on a binary Satisfactory / Unsatisfactory (Pass/Fail) basis without numerical GPA weight.
   - Set `grading_type: "percentage_gpa"` if standard letter grades (A+, A, B, etc.) and GPA points are awarded based on weighted percentages.

### OUTPUT SPECIFICATION
Respond strictly in valid JSON matching this schema:
{{
  "course_code": "{course_code}",
  "course_name": "Full Official Course Title",
  "credits": 3.0,
  "term": "Academic Term (e.g. Fall 2026)",
  "is_technical": true,
  "grading_type": "percentage_gpa",
  "grade_scale": "Seneca 4.0",
  "citation": "Document Title, Page X"
}}
Do NOT wrap your response in conversational text or markdown code fences. Return raw JSON only.
"""

def get_pass_2_categories_prompt(course_code: str, source_filename: str = "") -> str:
    source_constraint = f" in document '{source_filename}'" if source_filename else ""
    return f"""### ROLE & OBJECTIVE
You are an expert Academic Auditor verifying syllabus compliance and grading scheme integrity for **{course_code}**{source_constraint}.

### EXTRACTION DIRECTIVES
1. Locate the **"Modes of Evaluation"**, **"Evaluation Scheme"**, **"Marking Scheme"**, or **"Grading Policy"** section.
2. Identify every top-level assessment category (e.g., Labs, Practical Tests, Quizzes, Assignments, Midterm Exam, Final Exam, Projects, Management of Budget Allotment).
3. Extract the exact percentage weight assigned to each category.
4. **CRITICAL INTEGRITY CHECK**:
   - The sum of all category weights MUST equal exactly 100.0%.
   - If an asterisk or footnote indicates conditional or budget weights, detail how they contribute to the 100% total.

### OUTPUT SPECIFICATION
Respond strictly in valid JSON matching this schema:
{{
  "course_code": "{course_code}",
  "total_weight_verified": 100.0,
  "categories": [
    {{
      "category_id": "unique_lowercase_id (e.g. labs, tests, quizzes)",
      "name": "Official Category Name",
      "weight_percent": 40.0,
      "description": "Short description of what this category evaluates",
      "citation": "Page X, Section Y"
    }}
  ]
}}
Do NOT include conversational text. Return raw JSON only.
"""

def get_pass_3_items_prompt(course_code: str, source_filename: str = "") -> str:
    source_constraint = f" in document '{source_filename}'" if source_filename else ""
    return f"""### ROLE & OBJECTIVE
You are an Academic Operations Specialist creating a granular assessment tracker for **{course_code}**{source_constraint}.

### EXTRACTION DIRECTIVES
1. Cross-reference the **"Modes of Evaluation"** table with the **"Tentative Weekly Schedule"**, **"Topic Schedule"**, and assessment assignment lists.
2. Enumerate EVERY individual deliverable that contributes to the student's final grade:
   - Every individual lab (e.g., Lab 1, Lab 2 ... Lab 10)
   - Every individual quiz (e.g., Quiz 1, Quiz 2 ... Quiz 5)
   - Every individual assignment (e.g., Assignment 1, Assignment 2)
   - Every midterm, practical test, final test, or exam
   - Project milestones (e.g., Proposal, Presentation, Final Report)
3. For each deliverable, specify:
   - Item name and parent category ID
   - Exact percentage weight (e.g., 10 labs worth 40% total = 4.0% each)
   - Maximum points possible (default to 100 if unspecified)
   - Scheduled due date or calendar week (format YYYY-MM-DD or 'Week X' if explicit date is not given)

### OUTPUT SPECIFICATION
Respond strictly in valid JSON matching this schema:
{{
  "course_code": "{course_code}",
  "total_items_count": 14,
  "items": [
    {{
      "id": "{course_code.lower()}-lab-1",
      "category_id": "labs",
      "name": "Lab 1",
      "weight_percent": 4.0,
      "max_points": 100,
      "due_date": "2026-09-17",
      "scheduled_week": "Week 2",
      "citation": "Page X, Weekly Schedule"
    }}
  ]
}}
Do NOT include conversational text. Return raw JSON only.
"""

def get_pass_4_hurdles_prompt(course_code: str, source_filename: str = "") -> str:
    source_constraint = f" in document '{source_filename}'" if source_filename else ""
    return f"""### ROLE & OBJECTIVE
You are an Academic Standards and Appeals Officer auditing critical passing criteria and dual-criterion hurdles for **{course_code}**{source_constraint}.

### EXTRACTION DIRECTIVES
1. Carefully inspect the **"Note"**, **"Student Progression and Promotion Policy"**, **"To obtain a credit in this course"**, or asterisked footnotes beneath the evaluation table.
2. Identify all **Dual-Criterion Passing Hurdles** where a student can FAIL the course despite having an overall mathematically passing score (e.g. >= 50%). Common hurdles at Seneca include:
   - Mandatory test/exam sub-minimum (e.g., "Achieve a weighted average of 50% or higher on all tests/exams combined").
   - Mandatory lab sub-minimum (e.g., "Achieve a weighted average of 50% or higher on all labs").
   - Mandatory project completion or submission of all deliverables.
   - For SAT/UN courses: minimum passing score per knowledge check (e.g., >= 80% on each module).
3. Detail the exact consequences if a hurdle is not achieved (e.g., grade capped at F/49%, credit denied).

### OUTPUT SPECIFICATION
Respond strictly in valid JSON matching this schema:
{{
  "course_code": "{course_code}",
  "has_hurdles": true,
  "passing_criteria": [
    "Achieve an overall course grade of 50% or higher",
    "Achieve a weighted average of 50% or higher on all tests",
    "Satisfactorily complete all labs"
  ],
  "hurdles": [
    {{
      "type": "category_average",
      "target_category": "tests",
      "min_percentage": 50.0,
      "consequence": "Failure of course regardless of lab/assignment grades",
      "description": "Achieve a weighted average of 50% or higher on all tests",
      "citation": "Page X, Note 2"
    }}
  ]
}}
Do NOT include conversational text. Return raw JSON only.
"""

def get_pass_5_policies_prompt(course_code: str, source_filename: str = "") -> str:
    source_constraint = f" in document '{source_filename}'" if source_filename else ""
    return f"""### ROLE & OBJECTIVE
You are an Academic Policy Consultant analyzing course accommodations, exception handling, and drop policies for **{course_code}**{source_constraint}.

### EXTRACTION DIRECTIVES
1. Search for **"Drop Lowest Score"** policies:
   - Does the professor permit dropping the lowest quiz or lowest lab score? (e.g. 'best 8 of 10 labs counted'). If yes, specify the category and number of dropped items.
2. Search for **Late Submission Penalties**:
   - Extract the penalty percentage per day (e.g. 10% per day, maximum 3 days).
3. Search for **Missed Test & Assessment Policies**:
   - Look for policies regarding missed midterms (e.g. weight shifted to final exam vs doctor's note requirement).
4. Search for **Reference Sheets / Exam Aids**:
   - Note allowed aids (e.g. one 8.5x11 double-sided cheat sheet permitted on midterm/final).

### OUTPUT SPECIFICATION
Respond strictly in valid JSON matching this schema:
{{
  "course_code": "{course_code}",
  "drop_policies": [
    {{
      "category": "quizzes",
      "drop_lowest_n": 1,
      "description": "Lowest quiz score is dropped from calculation"
    }}
  ],
  "late_penalty_policy": "Description of late penalty or null",
  "exam_aids_allowed": "Description of allowed cheat sheets or null",
  "grade_scale": "Seneca 4.0",
  "citation": "Page X"
}}
Do NOT include conversational text. Return raw JSON only.
"""

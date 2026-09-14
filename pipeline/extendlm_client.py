"""
ExtendLM MCP Client & Multi-Pass Course Syllabus Extractor.

Connects to ExtendLM's remote Model Context Protocol (MCP) server
via Streamable HTTP (SSE) at https://mcp.extendlm.com/mcp to query
Gemini Notebook (NotebookLM) for class syllabus analysis.
"""

import json
import os
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

EXTENDLM_MCP_URL = os.environ.get("EXTENDLM_MCP_URL", "https://mcp.extendlm.com/mcp")

class ExtendLMClient:
    """Client for interacting with ExtendLM MCP server."""
    
    def __init__(self, base_url: str = EXTENDLM_MCP_URL, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token or os.environ.get("EXTENDLM_AUTH_TOKEN", "")
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "GradeCalculator-ExtendLM-Agent/1.0"
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calls an MCP tool on ExtendLM."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        req = urllib.request.Request(
            f"{self.base_url}/tools/call",
            data=json.dumps(payload).encode('utf-8'),
            headers=self.headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result.get("result", {})
        except urllib.error.URLError as e:
            return {"error": str(e), "status": "offline"}

    def ask_notebook(self, notebook_id: str, prompt: str, source_id: Optional[str] = None) -> str:
        """
        Queries NotebookLM with a targeted prompt.
        If source_id is provided, the query is strictly pinned/isolated to that source.
        """
        args = {
            "notebook_id": notebook_id,
            "question": prompt
        }
        if source_id:
            args["source_id"] = source_id
        res = self.call_tool("ask_notebook", args)
        if isinstance(res, dict) and "content" in res:
            return res["content"]
        return str(res)

    def extract_course_multi_pass(
        self,
        notebook_id: str,
        course_code: str,
        source_id: Optional[str] = None,
        source_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs 5 class-isolated passes against NotebookLM for a single course syllabus.
        Each pass targets a specific aspect of the grading contract to ensure 100% fidelity.
        """
        isolation_header = f"Focus EXCLUSIVELY on the course '{course_code}'"
        if source_name:
            isolation_header += f" from document '{source_name}'"
        isolation_header += ". Disregard all other courses.\n\n"

        # Pass 1: Course Identity & Scope
        prompt_p1 = (
            f"{isolation_header}"
            f"Pass 1 (Identity): What is the exact Course Code, Course Title, Credit Value, "
            f"Academic Term, and whether this is a technical computing course or general elective? "
            f"Also identify if grading is standard percentage GPA or SAT/UN (pass/fail). "
            f"Respond strictly in JSON format: {{\"course_code\": \"...\", \"course_name\": \"...\", "
            f"\"credits\": 3.0, \"is_technical\": true/false, \"grading_type\": \"percentage_gpa\"|\"sat_un\"}}"
        )
        res_p1 = self.ask_notebook(notebook_id, prompt_p1, source_id)

        # Pass 2: High-Level Evaluation Breakdown
        prompt_p2 = (
            f"{isolation_header}"
            f"Pass 2 (Categories): List every top-level assessment category (e.g. Labs, Quizzes, "
            f"Assignments, Midterm, Final Exam, Project, Budget) and its exact percentage weight. "
            f"The total sum of weights MUST equal 100%. "
            f"Respond strictly in JSON format: {{\"categories\": [{{\"name\": \"...\", \"weight_percent\": 40.0}}, ...]}}"
        )
        res_p2 = self.ask_notebook(notebook_id, prompt_p2, source_id)

        # Pass 3: Granular Assessment Items
        prompt_p3 = (
            f"{isolation_header}"
            f"Pass 3 (Itemized Assessments): List every individual lab, quiz, test, and assignment "
            f"with its specific weight percentage, maximum points, and scheduled due date (if present). "
            f"Respond strictly in JSON: {{\"items\": [{{\"category\": \"...\", \"name\": \"Lab 1\", "
            f"\"weight_percent\": 4.0, \"max_points\": 100, \"due_date\": \"YYYY-MM-DD\"|null}}, ...]}}"
        )
        res_p3 = self.ask_notebook(notebook_id, prompt_p3, source_id)

        # Pass 4: Passing Hurdles & Dual-Criterion Policies
        prompt_p4 = (
            f"{isolation_header}"
            f"Pass 4 (Passing Criteria & Hurdles): Are there specific passing hurdles required to earn credit? "
            f"E.g., must the student achieve >= 50% on tests/exams combined? Must all labs be completed? "
            f"List all explicit rules. "
            f"Respond strictly in JSON: {{\"passing_criteria\": [\"...\"], \"hurdles\": ["
            f"{{\"type\": \"category_average\"|\"all_completed\", \"target_category\": \"tests\", "
            f"\"min_percentage\": 50.0, \"description\": \"...\"}}]}}"
        )
        res_p4 = self.ask_notebook(notebook_id, prompt_p4, source_id)

        # Pass 5: Exceptions & Drop Policies
        prompt_p5 = (
            f"{isolation_header}"
            f"Pass 5 (Policies): Are there any 'drop lowest score' rules (e.g. drop lowest quiz), "
            f"late penalty rules, or special grading scales mentioned in this syllabus? "
            f"Respond in JSON: {{\"drop_rules\": [{{\"category\": \"...\", \"drop_lowest_n\": 1}}], "
            f"\"grade_scale\": \"Seneca 4.0\"}}"
        )
        res_p5 = self.ask_notebook(notebook_id, prompt_p5, source_id)

        return {
            "course_code": course_code,
            "pass_1_identity": res_p1,
            "pass_2_categories": res_p2,
            "pass_3_items": res_p3,
            "pass_4_hurdles": res_p4,
            "pass_5_policies": res_p5
        }

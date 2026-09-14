"""
ExtendLM MCP Client & Multi-Pass Course Syllabus Extractor.

Connects to ExtendLM's remote Model Context Protocol (MCP) server
via Streamable HTTP (SSE) at https://mcp.extendlm.com/mcp to query
Gemini Notebook (NotebookLM) for class syllabus analysis.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pipeline.notebooklm_prompts import (
    get_pass_1_identity_prompt,
    get_pass_2_categories_prompt,
    get_pass_3_items_prompt,
    get_pass_4_hurdles_prompt,
    get_pass_5_policies_prompt
)

EXTENDLM_MCP_URL = os.environ.get("EXTENDLM_MCP_URL", "https://mcp.extendlm.com/mcp")

class ExtendLMClient:
    """Client for interacting with ExtendLM MCP server."""
    
    def __init__(self, base_url: str = EXTENDLM_MCP_URL, auth_token: Optional[str] = None):
        self.base_url = base_url
        token_file = os.path.expanduser("~/.gemini/config/extendlm_token.json")
        file_token = ""
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as tf:
                    t_data = json.load(tf)
                    file_token = t_data.get("access_token", "")
            except Exception:
                pass
        self.auth_token = auth_token or os.environ.get("EXTENDLM_AUTH_TOKEN", "") or file_token
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

    def create_notebook(self, title: str) -> Dict[str, Any]:
        """Creates a new Gemini Notebook (NotebookLM)."""
        return self.call_tool("create_notebook", {"title": title})

    def list_notebooks(self) -> List[Dict[str, Any]]:
        """Lists available Gemini Notebooks."""
        res = self.call_tool("extendlm_list_notebooks_by_tag", {})
        return res.get("notebooks", [])

    def prepare_pdf_source_upload(self, notebook_id: str, filename: str) -> Dict[str, Any]:
        """Reserves a temporary grant-bound PDF source resource."""
        return self.call_tool("prepare_pdf_source_upload", {
            "notebook_id": notebook_id,
            "filename": filename
        })

    def add_pdf_source(self, notebook_id: str, resource_id: str) -> Dict[str, Any]:
        """Adds a previously prepared PDF resource to the notebook."""
        return self.call_tool("add_pdf_source", {
            "notebook_id": notebook_id,
            "resource_id": resource_id
        })

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
        Runs 5 class-isolated LLM passes against NotebookLM for a single course syllabus.
        Each pass employs an expertly framed persona, strict source grounding, and exact JSON schemas.
        """
        # Pass 1: Course Identity & Scope
        p1 = get_pass_1_identity_prompt(course_code, source_name or "")
        res_p1 = self.ask_notebook(notebook_id, p1, source_id)

        # Pass 2: Evaluation Category Breakdown (100% Total)
        p2 = get_pass_2_categories_prompt(course_code, source_name or "")
        res_p2 = self.ask_notebook(notebook_id, p2, source_id)

        # Pass 3: Granular Assessment Items
        p3 = get_pass_3_items_prompt(course_code, source_name or "")
        res_p3 = self.ask_notebook(notebook_id, p3, source_id)

        # Pass 4: Passing Criteria & Hurdles
        p4 = get_pass_4_hurdles_prompt(course_code, source_name or "")
        res_p4 = self.ask_notebook(notebook_id, p4, source_id)

        # Pass 5: Exceptions, Drop Lowest & Special Policies
        p5 = get_pass_5_policies_prompt(course_code, source_name or "")
        res_p5 = self.ask_notebook(notebook_id, p5, source_id)

        return {
            "course_code": course_code,
            "pass_1_identity": res_p1,
            "pass_2_categories": res_p2,
            "pass_3_items": res_p3,
            "pass_4_hurdles": res_p4,
            "pass_5_policies": res_p5
        }

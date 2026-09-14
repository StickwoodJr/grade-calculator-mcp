import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
ExtendLM MCP Client & Multi-Pass Course Syllabus Extractor.

Connects to ExtendLM's remote Model Context Protocol (MCP) server
via Streamable HTTP (SSE) at https://mcp.extendlm.com/mcp to interact with
Gemini Notebook (NotebookLM) for class syllabus analysis.
"""

import json
import secrets
import time
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
    """Production client for interacting with ExtendLM MCP server."""
    
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
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-11-25",
            "User-Agent": "GradeCalculator-ExtendLM-Agent/1.0"
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
        self._connection: Optional[str] = None
        self._user_id: Optional[str] = None

    def call_mcp(self, method: str, params: Dict[str, Any], rpc_id: int = 1, retries: int = 3) -> Dict[str, Any]:
        """Calls an MCP JSON-RPC method over SSE with automatic retry and exponential backoff."""
        payload = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params
        }
        
        last_err = None
        for attempt in range(1, retries + 1):
            req = urllib.request.Request(
                self.base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=self.headers,
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    raw = resp.read().decode("utf-8")
                    for line in raw.splitlines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            res = data.get("result", {})
                            if "content" in res and isinstance(res["content"], list):
                                first = res["content"][0]
                                if first.get("type") == "text":
                                    try:
                                        return json.loads(first.get("text", "{}"))
                                    except Exception:
                                        return {"text": first.get("text", "")}
                            return res
                    return {}
            except Exception as e:
                last_err = e
                print(f"    [!] MCP call warning (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(3 * attempt)
        
        return {"error": str(last_err), "status": "failed"}

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Calls a specific MCP tool by name."""
        return self.call_mcp("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

    def get_session_details(self) -> tuple:
        """Discovers or retrieves cached extension_connection and auth_user_id."""
        if self._connection and self._user_id:
            return self._connection, self._user_id

        res = self.call_tool("list_notebook_users", {})
        conns = res.get("connections", [])
        if not conns:
            raise RuntimeError("No active ExtendLM browser extension connection found.")
        self._connection = conns[0]["extension_connection"]
        users = conns[0].get("users", [])
        for u in users:
            if u.get("is_selected"):
                self._user_id = u.get("auth_user_id")
                break
        if not self._user_id and users:
            self._user_id = users[0].get("auth_user_id")
        return self._connection, self._user_id or "0"

    def list_notebooks(self) -> List[Dict[str, Any]]:
        """Lists available Gemini Notebooks."""
        conn, user_id = self.get_session_details()
        res = self.call_tool("list_notebooks", {
            "extension_connection": conn,
            "auth_user_id": user_id
        })
        return res.get("items", []) or res.get("notebooks", [])

    def create_notebook(self, title: str) -> Dict[str, Any]:
        """Creates a new Gemini Notebook (NotebookLM)."""
        conn, user_id = self.get_session_details()
        return self.call_tool("create_notebook", {
            "extension_connection": conn,
            "auth_user_id": user_id,
            "title": title,
            "idempotency_key": f"key-{secrets.token_hex(16)}"
        })

    def list_sources(self, notebook_id: str) -> List[Dict[str, Any]]:
        """Lists all sources attached to the notebook."""
        conn, user_id = self.get_session_details()
        res = self.call_tool("list_notebook_sources", {
            "extension_connection": conn,
            "auth_user_id": user_id,
            "notebook_id": notebook_id
        })
        return res.get("items", [])

    def upload_and_attach_pdf(self, notebook_id: str, filepath: str) -> Dict[str, Any]:
        """
        Uploads a local PDF to NotebookLM and attaches it to the notebook.
        Checks if the file title is already attached to avoid duplicate sources.
        """
        fname = os.path.basename(filepath)
        existing = self.list_sources(notebook_id)
        for src in existing:
            if src.get("title") == fname:
                return {
                    "status": "already_exists",
                    "filename": fname,
                    "source_id": src.get("id")
                }

        conn, user_id = self.get_session_details()
        
        # Step 1: Prepare upload
        prep = self.call_tool("prepare_pdf_source_upload", {
            "extension_connection": conn,
            "auth_user_id": user_id,
            "filename": fname
        })
        upload_url = prep.get("upload_url")
        req_headers = prep.get("required_headers", {})
        resource_id = prep.get("resource_id")

        if not upload_url or not resource_id:
            raise RuntimeError(f"Failed to prepare upload for {fname}: {prep}")

        # Step 2: Binary PUT
        with open(filepath, "rb") as f:
            data = f.read()

        put_req = urllib.request.Request(upload_url, data=data, headers=req_headers, method="PUT")
        with urllib.request.urlopen(put_req) as put_resp:
            if put_resp.status not in (200, 201):
                raise RuntimeError(f"PUT failed for {fname} with status {put_resp.status}")

        # Step 3: Attach to notebook
        add_res = self.call_tool("add_pdf_source", {
            "extension_connection": conn,
            "auth_user_id": user_id,
            "notebook_id": notebook_id,
            "resource_id": resource_id,
            "idempotency_key": f"key-{secrets.token_hex(16)}"
        })
        source_ids = add_res.get("source_ids", [])
        return {
            "status": "uploaded",
            "filename": fname,
            "source_id": source_ids[0] if source_ids else None,
            "details": add_res
        }

    def ask_notebook(
        self,
        notebook_id: str,
        question: str,
        source_ids: Optional[List[str]] = None
    ) -> str:
        """
        Queries Gemini Notebook with a targeted prompt.
        If source_ids is provided, the query is strictly pinned/isolated to those sources.
        """
        conn, user_id = self.get_session_details()
        args = {
            "extension_connection": conn,
            "auth_user_id": user_id,
            "notebook_id": notebook_id,
            "question": question
        }
        if source_ids:
            args["source_ids"] = source_ids

        res = self.call_tool("ask_notebook", args)
        if isinstance(res, dict):
            if "answer" in res:
                return res["answer"]
            if "text" in res:
                return res["text"]
            return json.dumps(res)
        return str(res)

    def extract_course_multi_pass(
        self,
        notebook_id: str,
        course_code: str,
        source_name: str,
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs 5 class-isolated LLM passes against NotebookLM for a single course syllabus.
        Each pass employs an expertly framed persona, strict source grounding, and exact JSON schemas.
        """
        s_ids = [source_id] if source_id else None

        print(f"  [Pass 1/5] Extracting Identity & Scope for {course_code}...")
        res_p1 = self.ask_notebook(notebook_id, get_pass_1_identity_prompt(course_code, source_name), s_ids)
        time.sleep(2)

        print(f"  [Pass 2/5] Extracting Category Breakdown for {course_code}...")
        res_p2 = self.ask_notebook(notebook_id, get_pass_2_categories_prompt(course_code, source_name), s_ids)
        time.sleep(2)

        print(f"  [Pass 3/5] Extracting Granular Assessment Items for {course_code}...")
        res_p3 = self.ask_notebook(notebook_id, get_pass_3_items_prompt(course_code, source_name), s_ids)
        time.sleep(2)

        print(f"  [Pass 4/5] Extracting Hurdles & Passing Rules for {course_code}...")
        res_p4 = self.ask_notebook(notebook_id, get_pass_4_hurdles_prompt(course_code, source_name), s_ids)
        time.sleep(2)

        print(f"  [Pass 5/5] Extracting Policies & Deadlines for {course_code}...")
        res_p5 = self.ask_notebook(notebook_id, get_pass_5_policies_prompt(course_code, source_name), s_ids)
        time.sleep(2)

        return {
            "course_code": course_code,
            "source_name": source_name,
            "source_id": source_id,
            "pass_1_identity": res_p1,
            "pass_2_categories": res_p2,
            "pass_3_items": res_p3,
            "pass_4_hurdles": res_p4,
            "pass_5_policies": res_p5
        }

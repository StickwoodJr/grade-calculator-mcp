#!/usr/bin/env python3
"""
Antigravity Stdio MCP Bridge for ExtendLM.

Exposes ExtendLM tools to Google Antigravity over stdio JSON-RPC:
- create_notebook
- list_notebooks
- prepare_pdf_source_upload
- add_pdf_source
- ask_notebook
"""

import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.extendlm_client import ExtendLMClient

client = ExtendLMClient()

TOOLS = [
    {
        "name": "create_notebook",
        "description": "Create a new Gemini Notebook (NotebookLM) notebook through ExtendLM.",
        "inputSchema": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string", "description": "Title for the new notebook"}
            }
        }
    },
    {
        "name": "list_notebooks",
        "description": "List all Gemini Notebook (NotebookLM) notebooks.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "prepare_pdf_source_upload",
        "description": "Reserve a temporary upload resource to add a PDF to a Gemini Notebook.",
        "inputSchema": {
            "type": "object",
            "required": ["notebook_id", "filename"],
            "properties": {
                "notebook_id": {"type": "string", "description": "Target notebook ID"},
                "filename": {"type": "string", "description": "Filename of PDF"}
            }
        }
    },
    {
        "name": "add_pdf_source",
        "description": "Attach an uploaded PDF resource to a Gemini Notebook.",
        "inputSchema": {
            "type": "object",
            "required": ["notebook_id", "resource_id"],
            "properties": {
                "notebook_id": {"type": "string", "description": "Target notebook ID"},
                "resource_id": {"type": "string", "description": "Resource ID from prepare_pdf_source_upload"}
            }
        }
    },
    {
        "name": "ask_notebook",
        "description": "Ask a question to Gemini Notebook (NotebookLM) with full source grounding.",
        "inputSchema": {
            "type": "object",
            "required": ["notebook_id", "question"],
            "properties": {
                "notebook_id": {"type": "string", "description": "Target notebook ID"},
                "question": {"type": "string", "description": "Question or prompt to query"},
                "source_id": {"type": "string", "description": "Optional source ID to isolate query to"}
            }
        }
    }
]

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "antigravity-extendlm-bridge",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": TOOLS
                }
            }
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "create_notebook":
                out = client.create_notebook(args.get("title", "Untitled"))
            elif name == "list_notebooks":
                out = client.list_notebooks()
            elif name == "prepare_pdf_source_upload":
                out = client.prepare_pdf_source_upload(args.get("notebook_id"), args.get("filename"))
            elif name == "add_pdf_source":
                out = client.add_pdf_source(args.get("notebook_id"), args.get("resource_id"))
            elif name == "ask_notebook":
                out = client.ask_notebook(args.get("notebook_id"), args.get("question"), args.get("source_id"))
            else:
                out = {"error": f"Unknown tool: {name}"}

            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(out, indent=2)}]
                }
            }
        else:
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }

        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()

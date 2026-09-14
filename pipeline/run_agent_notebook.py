#!/usr/bin/env python3
"""
End-to-End Live NotebookLM Orchestrator via ExtendLM MCP.

1. Connects to ExtendLM MCP server.
2. Creates or selects the Gemini Notebook: 'Seneca CTY Semester 3 Syllabi'.
3. Uploads local syllabus PDFs to NotebookLM.
4. Executes the 5-pass isolated LLM extraction sequence per course.
5. Saves extracted schemas to data/courses/ and compiles the Grade Calculator.
"""

import os
import sys
import json
import glob
import time
from pipeline.extendlm_client import ExtendLMClient

SYLLABI_DIR = "/home/gstickwood/gemini-projects/CTY Semester 3 Planning"

COURSE_MAPPING = [
    {"code": "CSN305", "file": "syllabi-2267-csn305-nbb-5197-loggedin.pdf"},
    {"code": "DAT330", "file": "syllabi-2267-dat330-nbb-5201-loggedin.pdf"},
    {"code": "MST300", "file": "syllabi-2267-mst300-nbb-5219-loggedin.pdf"},
    {"code": "PSY262", "file": "syllabi-2267-psy262-nbb-7086-loggedin.pdf"},
    {"code": "SEC320", "file": "syllabi-2267-sec320-nbb-5408-loggedin.pdf"},
    {"code": "OPS345", "file": "Welcome to OPS345 _ OPS345v2 - Open System Application Server.pdf"},
    {"code": "WTP100", "file": "WTP100.pdf"},
]

def main():
    print("=" * 70)
    print("ExtendLM MCP -> Gemini Notebook (NotebookLM) Live Orchestrator")
    print("=" * 70)

    client = ExtendLMClient()
    print(f"[*] Target MCP Server: {client.base_url}")

    # Check connection
    print("[*] Testing ExtendLM MCP connection...")
    notebooks = client.list_notebooks()
    print(f"[*] Available Notebooks: {len(notebooks)}")

    # Check or Create Notebook
    target_title = "Seneca CTY Semester 3 Syllabi"
    target_nb = None
    for nb in notebooks:
        if nb.get("title") == target_title:
            target_nb = nb
            break

    if not target_nb:
        print(f"[*] Creating new Gemini Notebook: '{target_title}'...")
        create_res = client.create_notebook(target_title)
        print(f"[*] Create Notebook Result: {create_res}")
        target_id = create_res.get("notebook_id") or create_res.get("id")
    else:
        target_id = target_nb.get("notebook_id") or target_nb.get("id")
        print(f"[*] Using existing Gemini Notebook: '{target_title}' (ID: {target_id})")

    if not target_id:
        print("[!] Note: Active OAuth grant is required to create notebooks in your account.")
        print("    Please authorize the connection via 'claude mcp login extendlm' or ExtendLM settings.")
        sys.exit(1)

    print(f"[✓] Active Notebook ID: {target_id}")

    # Upload local PDFs
    for item in COURSE_MAPPING:
        code = item["code"]
        fname = item["file"]
        fpath = os.path.join(SYLLABI_DIR, fname)
        if os.path.exists(fpath):
            print(f"[*] Uploading syllabus for {code} ({fname})...")
            # prepare_pdf_source_upload -> upload -> add_pdf_source
            prep = client.prepare_pdf_source_upload(target_id, fname)
            upload_url = prep.get("upload_url")
            resource_id = prep.get("resource_id")
            if upload_url:
                with open(fpath, "rb") as f:
                    data = f.read()
                import urllib.request
                req = urllib.request.Request(upload_url, data=data, method="PUT")
                urllib.request.urlopen(req)
                client.add_pdf_source(target_id, resource_id)
                print(f"    [✓] {code} source attached to NotebookLM.")

    # Execute 5-Pass Prompts per Course
    print("\n[*] Beginning 5-Pass Class-Isolated LLM Extraction Sequence...")
    for item in COURSE_MAPPING:
        code = item["code"]
        fname = item["file"]
        print(f"\n--- Extracting {code} (Passes 1 to 5) ---")
        extraction = client.extract_course_multi_pass(
            notebook_id=target_id,
            course_code=code,
            source_name=fname
        )
        print(f"    [✓] {code} 5-pass extraction completed.")

    print("\n[✓] All courses ingested. Re-compiling spreadsheet and web dashboard...")
    os.system("python3 pipeline/generate_sheets.py")
    os.system("npm run build --prefix web")

if __name__ == "__main__":
    main()

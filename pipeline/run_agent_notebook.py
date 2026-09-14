import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
End-to-End Live NotebookLM Orchestrator via ExtendLM MCP.

1. Connects to ExtendLM MCP server.
2. Creates or selects the Gemini Notebook: 'Seneca CTY Semester 3 Syllabi'.
3. Uploads local syllabus PDFs to NotebookLM with deduplication.
4. Executes the 5-pass isolated LLM extraction sequence per course, strictly pinning to each course's source ID.
5. Skips courses that have already been extracted to support seamless resumption.
6. Saves extracted prompt outputs to data/prompts_output/ and re-compiles the Grade Calculator.
"""

import json
import time
from pipeline.extendlm_client import ExtendLMClient

SYLLABI_DIR = "/home/gstickwood/gemini-projects/CTY Semester 3 Planning"
PROMPTS_OUTPUT_DIR = "/home/gstickwood/gemini-projects/Grade Calculator/data/prompts_output"

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
    print("=" * 75)
    print("  ExtendLM MCP -> Gemini Notebook (NotebookLM) Live Orchestrator")
    print("=" * 75)

    os.makedirs(PROMPTS_OUTPUT_DIR, exist_ok=True)
    client = ExtendLMClient()
    print(f"[*] Target MCP Server: {client.base_url}")

    # Discover session connection & user
    try:
        conn, user_id = client.get_session_details()
        print(f"[✓] Active ExtendLM Session: Connection={conn[:24]}... User={user_id}")
    except Exception as e:
        print(f"[!] ExtendLM connection error: {e}")
        sys.exit(1)

    # Check or Create Notebook
    target_title = "Seneca CTY Semester 3 Syllabi"
    notebooks = client.list_notebooks()
    target_nb = None
    for nb in notebooks:
        if nb.get("title") == target_title:
            target_nb = nb
            break

    if not target_nb:
        print(f"[*] Creating new Gemini Notebook: '{target_title}'...")
        create_res = client.create_notebook(target_title)
        target_id = create_res.get("notebook_id") or create_res.get("id")
    else:
        target_id = target_nb.get("notebook_id") or target_nb.get("id")

    if not target_id:
        print("[!] Error: Could not determine active notebook ID.")
        sys.exit(1)

    print(f"[✓] Active Notebook: '{target_title}' (ID: {target_id})")

    # Step 1: Upload syllabus PDFs to NotebookLM
    print("\n[*] Synchronizing Syllabus PDFs with NotebookLM...")
    existing_sources = {s.get("title"): s.get("id") for s in client.list_sources(target_id)}
    
    source_map = {}
    for item in COURSE_MAPPING:
        code = item["code"]
        fname = item["file"]
        fpath = os.path.join(SYLLABI_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[!] Warning: File not found: {fpath}")
            continue

        if fname in existing_sources:
            src_id = existing_sources[fname]
            print(f"  [✓] {code}: Already present in NotebookLM (Source ID: {src_id})")
            source_map[code] = src_id
        else:
            print(f"  [↑] {code}: Uploading {fname} to NotebookLM...")
            res = client.upload_and_attach_pdf(target_id, fpath)
            src_id = res.get("source_id")
            source_map[code] = src_id
            print(f"  [✓] {code}: Attached (Source ID: {src_id})")

    # Step 2: Execute 5-Pass Class-Isolated LLM Extraction Sequence
    print("\n[*] Executing 5-Pass Class-Isolated LLM Prompts...")
    for item in COURSE_MAPPING:
        code = item["code"]
        fname = item["file"]
        src_id = source_map.get(code)
        out_path = os.path.join(PROMPTS_OUTPUT_DIR, f"{code.lower()}_extraction.json")

        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print(f"  [⏩] {code}: Already successfully extracted -> skipping.")
            continue

        print(f"\n==========================================")
        print(f"  Querying Gemini Notebook for {code}")
        print(f"  Document Grounding: {fname} (ID: {src_id})")
        print(f"==========================================")

        extraction = client.extract_course_multi_pass(
            notebook_id=target_id,
            course_code=code,
            source_name=fname,
            source_id=src_id
        )

        with open(out_path, "w") as out_f:
            json.dump(extraction, out_f, indent=2)
        print(f"  [✓] Saved 5-pass results to {out_path}")

    print("\n[✓] All course extractions complete! Re-compiling spreadsheet and web dashboard...")
    os.system("python3 pipeline/generate_sheets.py")
    os.system("npm run build --prefix web")
    print("[✓] Pipeline execution finished successfully.")

if __name__ == "__main__":
    main()

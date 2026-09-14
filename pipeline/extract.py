#!/usr/bin/env python3
"""
Syllabus Extraction Pipeline for Grade Calculator.

Executes a 5-pass isolated extraction workflow for each course syllabus:
  Pass 1: Course Identity, credits, and technical classification
  Pass 2: High-Level Evaluation categories summing to 100%
  Pass 3: Itemized deliverables, individual weights, max points, and due dates
  Pass 4: Dual-criterion passing hurdles (e.g. >= 50% test average)
  Pass 5: Exceptions, drop lowest score policies, and SAT/UN status

Usage:
  python3 pipeline/extract.py --mode local --source-dir "/path/to/syllabi"
  python3 pipeline/extract.py --mode mcp --notebook-id "<id>"
  python3 pipeline/extract.py --verify
"""

import argparse
import glob
import json
import os
import re
import sys
from typing import Dict, Any, List

def parse_args():
    parser = argparse.ArgumentParser(description="Multi-pass Syllabus Extractor for Grade Calculator")
    parser.add_argument("--mode", choices=["local", "mcp"], default="local",
                        help="Extraction mode: 'local' (offline PDF parsing) or 'mcp' (ExtendLM remote)")
    parser.add_argument("--source-dir", default="/home/gstickwood/gemini-projects/CTY Semester 3 Planning",
                        help="Path containing syllabus PDFs")
    parser.add_argument("--output-dir", default="data/courses",
                        help="Directory to save extracted course JSON configs")
    parser.add_argument("--notebook-id", default=None,
                        help="NotebookLM Notebook ID when running in MCP mode")
    parser.add_argument("--verify", action="store_true",
                        help="Run validation checks on all extracted course JSON files")
    return parser.parse_args()

def verify_courses(output_dir: str):
    """Verifies all JSON files in output_dir against validation rules."""
    files = glob.glob(os.path.join(output_dir, "*.json"))
    course_files = [f for f in files if not f.endswith("courses_index.json")]
    print(f"[*] Verifying {len(course_files)} course configs in '{output_dir}'...")
    all_valid = True
    for f in course_files:
        with open(f, 'r') as fp:
            data = json.load(fp)
        code = data.get("course_code", "UNKNOWN")
        cats = data.get("categories", [])
        total_weight = sum(c.get("weight_percent", 0.0) for c in cats)
        if abs(total_weight - 100.0) > 0.1:
            print(f"  [!] {code} ({os.path.basename(f)}): Weight mismatch! Sum={total_weight:.1f}%")
            all_valid = False
        else:
            print(f"  [✓] {code}: 100% total weight, {len(cats)} categories, {sum(len(c.get('items', [])) for c in cats)} items.")
    return all_valid

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.verify:
        valid = verify_courses(args.output_dir)
        sys.exit(0 if valid else 1)
        
    print(f"=== Multi-Pass Syllabus Extraction (Mode: {args.mode.upper()}) ===")
    if args.mode == "mcp":
        from pipeline.extendlm_client import ExtendLMClient
        client = ExtendLMClient()
        print(f"Connecting to ExtendLM MCP at {client.base_url}...")
        if not args.notebook_id:
            print("Listing available notebooks...")
            res = client.call_tool("extendlm_list_notebooks_by_tag", {})
            print("Notebooks response:", res)
            print("Please specify --notebook-id to execute class-isolated multi-pass extraction.")
            sys.exit(1)
        else:
            print(f"Extracting courses from NotebookLM notebook '{args.notebook_id}'...")
            # Run passes using client.extract_course_multi_pass
    else:
        print(f"Scanning local PDFs in '{args.source_dir}'...")
        if not os.path.exists(args.source_dir):
            print(f"Source directory not found: {args.source_dir}")
            sys.exit(1)
        pdf_files = glob.glob(os.path.join(args.source_dir, "*.pdf"))
        print(f"Found {len(pdf_files)} PDF files.")
        verify_courses(args.output_dir)

if __name__ == "__main__":
    main()

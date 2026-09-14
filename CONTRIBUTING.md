# Contributing to Grade Calculator & ExtendLM MCP Pipeline

Thank you for your interest in contributing!

## Development Setup
1. Clone the repository.
2. Install Python dependencies: `pip install openpyxl jsonschema pypdf`.
3. Install Web dependencies: `npm install --prefix web`.

## Guidelines
- Follow the 5-pass isolated extraction methodology when adding new courses or universities.
- Run both test suites before submitting changes:
  ```bash
  python3 -m unittest discover tests/
  npm test --prefix web
  npm run build --prefix web
  ```
- Ensure all Excel formulas remain 100% compatible with Google Sheets.

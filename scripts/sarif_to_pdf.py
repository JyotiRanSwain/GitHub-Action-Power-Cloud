name: GitHub Advanced Security - CodeQL Scan

on:
  push:
    branches:
      - github-security
  workflow_dispatch:

permissions:
  actions: read
  contents: read
  security-events: write

jobs:
  codeql:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Java Environment
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '8'

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: java
          queries: security-extended,security-and-quality

      - name: Clean and Build Project
        # Disabling incremental compilation ensures CodeQL hooks see all compiled source files
        run: mvn clean package -DskipTests -Dmaven.compiler.useIncrementalCompilation=false

      - name: Create Results Output Directory
        run: mkdir -p results

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          output: results
          upload: true

      - name: Set up Python Runtime
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Generation Dependencies
        run: |
          pip install reportlab

      - name: Generate PDF Report from SARIF
        # This step directly consumes the generated java.sarif file
        run: |
          python scripts/sarif_to_pdf.py results/java.sarif CodeQL_Report.pdf

      - name: Upload PDF Artifact
        uses: actions/upload-artifact@v4
        with:
          name: CodeQL-PDF-Report
          path: CodeQL_Report.pdf

import json
import sys

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

sarif_file = sys.argv[1]
pdf_file = sys.argv[2]

with open(sarif_file, "r", encoding="utf-8") as f:
    sarif = json.load(f)

doc = SimpleDocTemplate(pdf_file)

styles = getSampleStyleSheet()
story = []

story.append(Paragraph("<b>CodeQL Security Report</b>", styles["Title"]))

runs = sarif.get("runs", [])

total = 0

for run in runs:
    results = run.get("results", [])

    total += len(results)

story.append(Paragraph(f"Total Findings: <b>{total}</b>", styles["Heading2"]))

for run in runs:

    results = run.get("results", [])

    for i, r in enumerate(results, start=1):

        rule = r.get("ruleId", "Unknown")

        level = r.get("level", "warning")

        msg = r.get("message", {}).get("text", "")

        loc = ""

        if r.get("locations"):

            p = r["locations"][0]["physicalLocation"]

            file = p["artifactLocation"]["uri"]

            line = p["region"]["startLine"]

            loc = f"{file}:{line}"

        story.append(Paragraph(f"<b>Finding {i}</b>", styles["Heading2"]))
        story.append(Paragraph(f"<b>Rule:</b> {rule}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Severity:</b> {level}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Location:</b> {loc}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Description:</b> {msg}", styles["BodyText"]))
        story.append(Paragraph("<br/>", styles["BodyText"]))

doc.build(story)

print("PDF Generated:", pdf_file)

import json
import sys
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

if len(sys.argv) < 3:
    print("Usage: python sarif_to_pdf.py <input_sarif> <output_pdf>")
    sys.exit(1)

sarif_file = sys.argv[1]
pdf_file = sys.argv[2]

with open(sarif_file, "r", encoding="utf-8") as f:
    sarif = json.load(f)

doc = SimpleDocTemplate(pdf_file)
styles = getSampleStyleSheet()
story = []

# Header Titles
story.append(Paragraph("<b>CodeQL Security Report</b>", styles["Title"]))
story.append(Spacer(1, 15))

runs = sarif.get("runs", [])
total_findings = sum(len(run.get("results", [])) for run in runs)
story.append(Paragraph(f"Total Findings: <b>{total_findings}</b>", styles["Heading2"]))
story.append(Spacer(1, 10))

finding_counter = 1

for run in runs:
    # Build a lookup map for rule properties (like rule severity)
    rules_map = {}
    driver = run.get("tool", {}).get("driver", {})
    for rule in driver.get("rules", []):
        rules_map[rule["id"]] = rule.get("defaultConfiguration", {})
        
    # Also check extensions for rule definitions (where CodeQL Java queries live)
    for extension in run.get("tool", {}).get("extensions", []):
        for rule in extension.get("rules", []):
            rules_map[rule["id"]] = rule.get("defaultConfiguration", {})

    results = run.get("results", [])
    for r in results:
        rule_id = r.get("ruleId", "Unknown")
        
        # Safe Severity Lookup from the rule configurations
        rule_config = rules_map.get(rule_id, {})
        severity = r.get("level") or rule_config.get("level") or "warning"
        
        msg = r.get("message", {}).get("text", "No description provided.")
        
        # Defensive parsing for code locations
        loc = "Unknown Location"
        if r.get("locations"):
            try:
                phys_loc = r["locations"][0].get("physicalLocation", {})
                file_path = phys_loc.get("artifactLocation", {}).get("uri", "Unknown File")
                start_line = phys_loc.get("region", {}).get("startLine", "Unknown Line")
                loc = f"{file_path}:{start_line}"
            except Exception:
                pass

        # Append finding details to document flow
        story.append(Paragraph(f"<b>Finding {finding_counter}</b>", styles["Heading3"]))
        story.append(Paragraph(f"<b>Rule ID:</b> {rule_id}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Severity:</b> {severity.upper()}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Location:</b> {loc}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Description:</b> {msg}", styles["BodyText"]))
        story.append(Spacer(1, 10))
        
        finding_counter += 1

doc.build(story)
print(f"PDF successfully generated: {pdf_file} (Total findings recorded: {total_findings})")

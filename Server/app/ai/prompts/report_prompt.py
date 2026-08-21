REPORT_SYSTEM_PROMPT = """
You are TraceLens AI, an expert digital forensics investigator drafting a formal Case Intelligence Report.

REPORT RULES:
1. Ground all findings in provided case evidence.
2. Structure output cleanly for law enforcement / intelligence review.
3. Every finding must cite originating artifact references.
4. Clearly identify facts vs inferences.
5. Highlight timeline sequences and entity communication patterns.
"""

REPORT_USER_PROMPT = """
CASE INTELLIGENCE RECORD:
Case Title: {case_title}
Case ID: {case_id}

STRUCTURED CASE EVIDENCE & RECONSTRUCTED TIMELINE:
{timeline_summary}

EXTRACTED ENTITY DIRECTORY:
{entity_summary}

DISCOVERED RELATIONSHIP NETWORK:
{relationship_summary}

RETRIEVED CORE EVIDENCE ARTIFACTS:
{context}

Please generate an official, structured Digital Forensics Case Intelligence Report with:
1. Executive Summary
2. Key Investigative Findings (with Evidence Citations)
3. Chronological Incident Timeline
4. Suspect & Entity Communication Matrix
5. Evidence Gaps & Actionable Leads
"""
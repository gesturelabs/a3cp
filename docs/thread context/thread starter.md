We will build the file:

apps/landmark_extractor/service.py

Important instructions:

1. Do NOT generate any Python code unless explicitly instructed.
2. Do NOT infer missing architecture.
3. Do NOT rewrite specifications.
4. Only analyze and confirm alignment between the specification and the outline.
5. If something is unclear, ask for clarification instead of guessing.
6. Do NOT refactor or reorganize the outline unless explicitly asked.
7. Do not output example implementations or pseudo-code.

Workflow for this thread:

Step 1 — I will paste reference files and specifications.
Step 2 — Confirm understanding and check for:
    - architectural inconsistencies
    - missing responsibilities
    - contract violations
Step 3 — Verify that the outline fully satisfies the specification.
Step 4 — Only after the outline is confirmed will we generate code blocks one section at a time.

Generation rules when we reach that stage:

• Only generate the requested section.
• Do not generate the entire file.
• Do not modify earlier sections unless asked.
• Keep helper functions private unless explicitly required.

Context order I will provide:

1. service.py outline
2. service.py specification / TODO
3. schema definitions
4. artifact writer contract
5. schema recorder contract
6. domain types
7. backend interface
8. feature-row builder
9. config constants

Your role initially is ONLY to review alignment between the spec and the outline.

Wait for the files.
Do not generate code yet.

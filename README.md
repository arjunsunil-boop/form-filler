# Form Filler

Simple script that auto‑generates synthetic accessibility survey responses with Gemini and submits them to a Google Form. It maps generated JSON fields to the form's `entry.<id>` parameters and posts them using `requests`.

Basic flow:
1. Generate one JSON response (Gemini).
2. Sanitize + enforce allowed choices.
3. Build payload with form field IDs.
4. POST to the form endpoint repeatedly.

To use: set a valid `FORM_URL`, put your Gemini API key in `filler.py`, adjust `NUM_RESPONSES`, then run:
```cmd
python filler.py
```

Only synthetic data should be submitted.

# Form Filler

Simple script that auto‑generates synthetic accessibility survey responses with Gemini and submits them to a Google Form. It maps generated JSON fields to the form's `entry.<id>` parameters and posts them using `requests`.

Basic flow:
1. Generate one JSON response (Gemini).
2. Sanitize + enforce allowed choices.
3. Build payload with form field IDs.
4. POST to the form endpoint repeatedly.

## Quick Setup

1. **Get entry field IDs and formResponse URL** from your Google Form page source:
   - Open your form in a browser
   - Press `Ctrl+U` (or right-click → View Page Source)
   - Search for `entry.` to find all field IDs (e.g., `entry.1791513292`)
   - Search for `formResponse` to find the POST endpoint (looks like `https://docs.google.com/forms/d/e/<FORM_ID>/formResponse`)
   - Update `ENTRY` dict and `FORM_URL` in `filler.py`

2. Set your Gemini API key:
   - Replace `"api here"` in `filler.py` with your actual key
   - Or use env var: `set GENAI_API_KEY=YOUR_KEY_HERE`

3. Adjust `NUM_RESPONSES` if needed, then run:
   ```cmd
   python filler.py
   ```

Only synthetic data should be submitted.

import requests
import time
import random
import json
from google import genai

# ================= CONFIG =================

# Google Form POST URL (from your form HTML)
FORM_URL = "googleforms/formResponse"

# Gemini client
client = genai.Client(api_key="api here")

# How many responses you want
NUM_RESPONSES = 7

# Entry IDs for your form
ENTRY = {
    "full_name": "entry.1791513292",
    "age": "entry.1979291121",
    "gender": "entry.1291398386",
    "occupation": "entry.845666920",
    "email": "entry.1811303397",
    "user_type": "entry.1597699878",

    "challenges": "entry.1943546820",
    "frequency": "entry.225527121",
    "tools_support": "entry.1544352811",
    "tools_support_sentinel": "entry.1544352811_sentinel",
    "satisfaction": "entry.973558319",
    "methods": "entry.295035322",
    "methods_sentinel": "entry.295035322_sentinel",
    "improvements": "entry.424804704",
    "important_features": "entry.313957006",
    "important_features_sentinel": "entry.313957006_sentinel",
    "usefulness": "entry.32541131",
    "concerns": "entry.71697414",
    "prototype_interest": "entry.1698936070",
    "comments": "entry.1827507365",
}

# Hidden constants from the form HTML
HIDDEN_CONSTANTS = {
    "fvv": "1",
    "partialResponse": '[null,null,"8858451967529929482"]',
    "pageHistory": "0",
    "fbzx": "1800927083085286005",
    "submissionTimestamp": "-1",
}

# Allowed option sets (from your form)
ALLOWED_GENDERS = {"Female", "Male", "Non-binary", "Prefer not to say"}
ALLOWED_USER_TYPES = {
    "Visually Impaired Person",
    "Caregiver or Family Member",
    "Retail Staff",
    "General Customer or User",
    "Other",
}
ALLOWED_FREQUENCIES = {"Daily", "Weekly", "Monthly", "Rarely", "Never"}

ALLOWED_TOOLS = {
    "Human Assistance",
    "Mobile Apps",
    "Assistive Technology",
    "Memory/Familiarity",
    "None",
    "Other",
}
ALLOWED_METHODS = {
    "Manual effort",
    "Technology or apps",
    "Asking for help",
    "I do not use any solution",
    "Other",
}
ALLOWED_FEATURES = {
    "Accuracy",
    "Ease of Use",
    "Speed",
    "Affordability",
    "Privacy",
    "Portability",
    "Convenience",
}
ALLOWED_PROTOTYPE_INTEREST = {"Yes", "No"}

# Track uniqueness for personal fields
USED_NAMES = set()
USED_EMAILS = set()

# ================= PER-USER-TYPE TEXT POOLS =================

VIP_CHALLENGES = [
    "I find it very hard to identify products or read labels on my own inside supermarkets.",
    "I cannot see expiry dates, prices or ingredients clearly, so I have to ask for help almost every time.",
    "I feel unsure if I picked the correct product because I cannot access the visual information on the shelves.",
    "I struggle to locate the correct aisle or shelf without someone guiding me.",
]

VIP_IMPROVEMENTS = [
    "A tool that can identify products and read details aloud in real time would help me shop more independently.",
    "I would like a system that can guide me to the right shelf and tell me the product, price and expiry clearly.",
    "Technology that checks ingredients and suitability for my health condition would be very helpful.",
    "A simple wearable device that tells me what is in front of me and where to go would reduce my dependence on others.",
]

CAREGIVER_CHALLENGES = [
    "I often have to read every label and explain products in detail to the person I support.",
    "Shopping takes longer because I need to guide them through every aisle and help them choose safely.",
    "If I am busy, it becomes difficult for them to shop at all without my help.",
]

CAREGIVER_IMPROVEMENTS = [
    "A system that gives them clear audio guidance would reduce the amount of support they need from me.",
    "I would like technology that can tell them product details so I do not have to read everything for them.",
    "If they could navigate and identify items more independently, it would make shopping easier for both of us.",
]

STAFF_CHALLENGES = [
    "Visually impaired customers often ask for help to find products or read labels, which takes extra time.",
    "It is difficult to always be available to guide them when the store is busy.",
    "Sometimes it is hard to explain the exact location or details of products in a clear way.",
]

STAFF_IMPROVEMENTS = [
    "A solution that helps customers find products on their own would reduce their dependency on staff.",
    "If there was a system that could read product information for them, our support would be more efficient.",
    "Technology that guides visually impaired customers to the correct shelf would make the store more inclusive.",
]

GENERAL_CHALLENGES = [
    "I see that people with visual difficulties struggle a lot with reading labels and finding items in shops.",
    "I feel current systems are not accessible enough for visually impaired customers.",
]

GENERAL_IMPROVEMENTS = [
    "New technology that supports visually impaired people in stores would make shopping more equal for everyone.",
    "I would like to see solutions that give them more independence and confidence while shopping.",
]

# ================= GEMINI GENERATION =================

def generate_record_raw():
    """
    Ask Gemini to generate one synthetic response in strict JSON.
    We pass already-used names/emails so Gemini avoids repeats.
    """

    used_names_str = ", ".join(sorted(USED_NAMES)) or "none"
    used_emails_str = ", ".join(sorted(USED_EMAILS)) or "none"

    prompt = f"""
Generate a single synthetic user survey response in pure JSON only.
Do not include any extra text or markdown.

Avoid using these names: {used_names_str}
Avoid using these emails: {used_emails_str}

Use exactly this JSON structure:

{{
  "full_name": "Fictional Kerala (Malayali) name from India (not from the avoid list, and not a public figure)",
  "age": "number 18-60",
  "gender": "Female or Male or Non-binary or Prefer not to say",
  "occupation": "Short job title",
  "email": "unique Gmail address using the person's name, like firstname.lastname###@gmail.com, and not in the avoid list",

  "user_type": "Visually Impaired Person or Caregiver or Family Member or Retail Staff or General Customer or User or Other",

  "challenges": "1–2 short sentences",
  "frequency": "Daily or Weekly or Monthly or Rarely or Never",

  "tools_support": [
    "Human Assistance, Mobile Apps, Assistive Technology, Memory/Familiarity, None, Other"
  ],

  "satisfaction": "1–5",
  "methods": [
    "Manual effort, Technology or apps, Asking for help, I do not use any solution, Other"
  ],

  "improvements": "1–2 short sentences",
  "important_features": [
    "Accuracy, Ease of Use, Speed, Affordability, Privacy, Portability, Convenience"
  ],

  "usefulness": "1–10",
  "concerns": "1–2 short sentences",
  "prototype_interest": "Yes or No",
  "comments": "0–2 short sentences"
}}

Rules:
- Use realistic Kerala/Malayali names from India, but do not use names of celebrities or well-known public figures.
- Use only fictional data.
- Email MUST be a gmail.com address based on the name, not in the avoid list.
- Keep answers short and natural.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = (response.text or "").strip()

    # Strip ```json ... ``` if present
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)

# ================= SANITISERS =================

def ensure_non_empty(value, fallback):
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback

def ensure_choice(value, allowed_set, fallback=None):
    v = (value or "").strip()
    if v in allowed_set:
        return v
    return fallback if fallback is not None else random.choice(list(allowed_set))

def ensure_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []

def ensure_list_from_allowed(values, allowed_set, min_items=1, max_items=3):
    items = ensure_list(values)
    filtered = [v for v in items if v in allowed_set]
    if not filtered:
        k = random.randint(min_items, min(max_items, len(allowed_set)))
        filtered = random.sample(list(allowed_set), k)
    return filtered

def ensure_int_range(value, min_v, max_v, default=None):
    try:
        iv = int(str(value).strip())
        if min_v <= iv <= max_v:
            return str(iv)
    except Exception:
        pass
    if default is not None:
        return str(default)
    return str(random.randint(min_v, max_v))

def sanitize_record(raw):
    """
    Take raw JSON from Gemini and normalise it so every field
    matches the form's allowed formats and ranges.
    """
    r = raw.copy()

    r["full_name"] = ensure_non_empty(
        r.get("full_name", ""),
        f"User {random.randint(1000, 9999)}"
    )
    r["age"] = ensure_int_range(r.get("age", "25"), 18, 60, default=25)
    r["gender"] = ensure_choice(r.get("gender", ""), ALLOWED_GENDERS)
    r["occupation"] = ensure_non_empty(r.get("occupation", ""), "Student")

    # Email: ensure gmail, and non-empty
    email = r.get("email", "").strip()
    if not email or "@gmail.com" not in email:
        base = r["full_name"].lower().replace(" ", ".")
        email = f"{base}{random.randint(1,999)}@gmail.com"
    r["email"] = email

    # User type: keep whatever Gemini gave if valid, otherwise random
    # Weighted user type selection:
    # ~50% Visually Impaired Person, ~50% random from all types

    ut_raw = r.get("user_type", "").strip()

    # 50% chance to force "Visually Impaired Person"
    if random.random() < 0.5:
        r["user_type"] = "Visually Impaired Person"
    else:
        # If Gemini gave a valid type, keep it. Otherwise random.
        r["user_type"] = ensure_choice(ut_raw, ALLOWED_USER_TYPES)

    ut = r["user_type"]



    # Challenges and improvements based on user type, focused on need for new tech
    if ut == "Visually Impaired Person":
        r["challenges"] = random.choice(VIP_CHALLENGES)
        r["improvements"] = random.choice(VIP_IMPROVEMENTS)
    elif ut == "Caregiver or Family Member":
        r["challenges"] = random.choice(CAREGIVER_CHALLENGES)
        r["improvements"] = random.choice(CAREGIVER_IMPROVEMENTS)
    elif ut == "Retail Staff":
        r["challenges"] = random.choice(STAFF_CHALLENGES)
        r["improvements"] = random.choice(STAFF_IMPROVEMENTS)
    elif ut == "General Customer or User":
        r["challenges"] = random.choice(GENERAL_CHALLENGES)
        r["improvements"] = random.choice(GENERAL_IMPROVEMENTS)
    else:
        r["challenges"] = "I see that there are still many accessibility gaps in this area."
        r["improvements"] = "New technology that focuses on accessibility would make a big difference."

    r["frequency"] = ensure_choice(
        r.get("frequency", ""),
        ALLOWED_FREQUENCIES,
        fallback="Weekly",
    )

    r["tools_support"] = ensure_list_from_allowed(
        r.get("tools_support", []),
        ALLOWED_TOOLS,
        min_items=1,
        max_items=3,
    )

    # Low satisfaction to show need for new tech (1–3)
    r["satisfaction"] = ensure_int_range(
        r.get("satisfaction", "2"), 1, 3, default=2
    )

    r["methods"] = ensure_list_from_allowed(
        r.get("methods", []),
        ALLOWED_METHODS,
        min_items=1,
        max_items=3,
    )

    r["important_features"] = ensure_list_from_allowed(
        r.get("important_features", []),
        ALLOWED_FEATURES,
        min_items=2,
        max_items=4,
    )

    # High usefulness for a better solution (8–10)
    r["usefulness"] = ensure_int_range(
        r.get("usefulness", "9"), 8, 10, default=9
    )

    r["concerns"] = ensure_non_empty(
        r.get("concerns", ""),
        "I would be concerned about privacy, cost and whether the technology works reliably in real situations.",
    )

    r["prototype_interest"] = ensure_choice(
        r.get("prototype_interest", ""),
        ALLOWED_PROTOTYPE_INTEREST,
        fallback="Yes",
    )

    # comments can be empty
    r["comments"] = r.get("comments", "").strip()

    return r

# ================= PAYLOAD BUILD =================

def build_payload(record):
    payload = dict(HIDDEN_CONSTANTS)

    # Simple fields
    payload[ENTRY["full_name"]] = record["full_name"]
    payload[ENTRY["age"]] = record["age"]
    payload[ENTRY["gender"]] = record["gender"]
    payload[ENTRY["occupation"]] = record["occupation"]
    payload[ENTRY["email"]] = record["email"]
    payload[ENTRY["user_type"]] = record["user_type"]

    payload[ENTRY["challenges"]] = record["challenges"]
    payload[ENTRY["frequency"]] = record["frequency"]
    payload[ENTRY["satisfaction"]] = record["satisfaction"]
    payload[ENTRY["improvements"]] = record["improvements"]
    payload[ENTRY["usefulness"]] = record["usefulness"]
    payload[ENTRY["concerns"]] = record["concerns"]
    payload[ENTRY["prototype_interest"]] = record["prototype_interest"]
    payload[ENTRY["comments"]] = record["comments"]

    # Checkbox fields (lists)
    payload[ENTRY["tools_support"]] = record["tools_support"]
    payload[ENTRY["methods"]] = record["methods"]
    payload[ENTRY["important_features"]] = record["important_features"]

    # Sentinel fields (must exist, even if empty)
    payload[ENTRY["tools_support_sentinel"]] = ""
    payload[ENTRY["methods_sentinel"]] = ""
    payload[ENTRY["important_features_sentinel"]] = ""

    return payload

# ================= SUBMISSION LOOP =================

def submit_one():
    try:
        raw = generate_record_raw()
    except Exception as e:
        print("Gemini error, skipping:", e)
        return

    record = sanitize_record(raw)

    # Enforce uniqueness for name and email
    base_name = record["full_name"]
    base_email = record["email"]

    # Make name unique if needed by appending a number
    name = base_name
    suffix = 1
    while name in USED_NAMES:
        name = f"{base_name} {suffix}"
        suffix += 1
    record["full_name"] = name
    USED_NAMES.add(name)

    # Make email unique if needed
    email = base_email
    while email in USED_EMAILS:
        local, _, domain = base_email.partition("@")
        if not domain:
            domain = "gmail.com"
        email = f"{local}{random.randint(1,9999)}@{domain}"
    record["email"] = email
    USED_EMAILS.add(email)

    payload = build_payload(record)

    resp = requests.post(FORM_URL, data=payload)
    print(f"Submitted for {record['full_name']}  |  {record['email']}  |  status {resp.status_code}")

if __name__ == "__main__":
    for _ in range(NUM_RESPONSES):
        submit_one()
        time.sleep(random.uniform(1, 3))

import os
import requests
print("******** google_sheet.py loaded ********")

# ==========================
# Load .env manually
# ==========================
print("google_sheet.py loaded successfully")
env_paths = [
    ".env",
    "backend/.env",
    os.path.join(os.path.dirname(__file__), ".env")
]

for path in env_paths:
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()

                if (
                    line
                    and not line.startswith("#")
                    and "=" in line
                ):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

        print(f"Loaded environment from: {path}")
        break

# ==========================
# Google Apps Script URL
# ==========================

WEBAPP_URL = os.environ.get(
    "GOOGLE_SHEET_WEBAPP_URL",
    "YOUR_GOOGLE_APPS_SCRIPT_WEBAPP_URL_HERE"
)
print("Loaded WEBAPP_URL:", WEBAPP_URL)

# ==========================
# Register User
# ==========================

def register_user_in_sheet(username, password):

    if (
        not WEBAPP_URL
        or "YOUR_GOOGLE_APPS_SCRIPT_WEBAPP_URL" in WEBAPP_URL
    ):
        print("Warning: Google Sheets URL not configured.")
        return {
            "status": "error",
            "error": "Google Sheets URL not configured"
        }

    try:

        data = {
            "action": "register",
            "username": username,
            "password": password
        }

        print("\n" + "=" * 60)
        print("REGISTER REQUEST")
        print("WEBAPP_URL =", WEBAPP_URL)
        print("DATA =", data)

        response = requests.post(
            WEBAPP_URL,
            data=data,
            timeout=15
        )

        print("STATUS =", response.status_code)
        print("BODY =", response.text)
        print("=" * 60 + "\n")

        if response.status_code == 200:
            return response.json()

        return {
            "status": "error",
            "error": f"HTTP error {response.status_code}"
        }

    except Exception as e:
        print("REGISTER EXCEPTION =", str(e))
        return {
            "status": "error",
            "error": str(e)
        }

# ==========================
# Login User
# ==========================

def validate_user_in_sheet(username, password):

    if (
        not WEBAPP_URL
        or "YOUR_GOOGLE_APPS_SCRIPT_WEBAPP_URL" in WEBAPP_URL
    ):
        print("Warning: Google Sheets URL not configured.")
        return False

    try:

        data = {
            "action": "login",
            "username": username,
            "password": password
        }

        print("\n" + "=" * 60)
        print("LOGIN REQUEST")
        print("DATA =", data)

        response = requests.post(
            WEBAPP_URL,
            data=data,
            timeout=15
        )

        print("STATUS =", response.status_code)
        print("BODY =", response.text)
        print("=" * 60 + "\n")

        if response.status_code == 200:
            res = response.json()
            return res.get("status") == "success"

        return False

    except Exception as e:
        print("LOGIN EXCEPTION =", str(e))
        return False

# ==========================
# Save Stock Result
# ==========================

def save_analysis_result(
    stock_name,
    current_price,
    fair_value,
    profit
):

    if (
        not WEBAPP_URL
        or "YOUR_GOOGLE_APPS_SCRIPT_WEBAPP_URL" in WEBAPP_URL
    ):
        print("Warning: Google Sheets URL not configured.")
        return {
            "status": "error",
            "error": "Google Sheets URL not configured"
        }

    try:

        data = {
            "action": "save_result",
            "stock_name": stock_name,
            "current_price": str(current_price),
            "fair_value": str(fair_value),
            "profit": str(profit)
        }

        response = requests.post(
            WEBAPP_URL,
            data=data,
            timeout=15
        )

        print("\nSAVE RESULT")
        print("STATUS =", response.status_code)
        print("BODY =", response.text)

        if response.status_code == 200:
            return response.json()

        return {
            "status": "error",
            "error": f"HTTP error {response.status_code}"
        }

    except Exception as e:
        print("SAVE RESULT EXCEPTION =", str(e))
        return {
            "status": "error",
            "error": str(e)
        }

# ==========================
# Get History
# ==========================

def get_analysis_history():

    if (
        not WEBAPP_URL
        or "YOUR_GOOGLE_APPS_SCRIPT_WEBAPP_URL" in WEBAPP_URL
    ):
        print("Warning: Google Sheets URL not configured.")
        return []

    try:

        data = {
            "action": "get_results"
        }

        response = requests.post(
            WEBAPP_URL,
            data=data,
            timeout=15
        )

        print("\nGET HISTORY")
        print("STATUS =", response.status_code)
        print("BODY =", response.text)

        if response.status_code == 200:

            res = response.json()

            if res.get("status") == "success":
                return res.get("data", [])

        return []

    except Exception as e:
        print("GET HISTORY EXCEPTION =", str(e))
        return []
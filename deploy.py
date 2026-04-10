"""
Deploy the Masters Flashcard App to Posit Connect Cloud.

Requires two environment variables (set in a .env file or your shell):
  CONNECT_SERVER   - e.g. https://connect.posit.cloud/mc-scott
  CONNECT_API_KEY  - your Posit Connect API key

Usage:
  python deploy.py
"""

import os
import sys

from dotenv import load_dotenv
from rsconnect.api import RSConnectServer
from rsconnect.actions import deploy_python_api

load_dotenv()

CONNECT_SERVER = os.environ.get("CONNECT_SERVER")
CONNECT_API_KEY = os.environ.get("CONNECT_API_KEY")

if not CONNECT_SERVER or not CONNECT_API_KEY:
    sys.exit(
        "ERROR: CONNECT_SERVER and CONNECT_API_KEY must be set "
        "(in a .env file or as environment variables)."
    )

# --- Connect ---------------------------------------------------------------
# Equivalent CLI command:
#   rsconnect add --server $CONNECT_SERVER --api-key $CONNECT_API_KEY --name posit-cloud

print(f"Connecting to {CONNECT_SERVER} ...")
server = RSConnectServer(url=CONNECT_SERVER, api_key=CONNECT_API_KEY)

# --- Deploy ----------------------------------------------------------------
# Equivalent CLI command:
#   rsconnect deploy api --server posit-cloud --entrypoint app:app --title "Masters Flashcard App" .

print("Deploying Flask app ...")
deploy_python_api(
    connect_server=server,
    directory=".",
    entrypoint="app:app",
    title="Masters Flashcard App",
    extra_files=["cards.yaml"],
)

print("Deployment complete.")

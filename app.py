import glob
import os
import random
import sys
from datetime import datetime, timezone
import markdown as md
import yaml
from flask import Flask, redirect, render_template, request, session, url_for
from markupsafe import Markup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SESSION_TIMEOUT_HOURS = 4
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SESSION_TIMEOUT_HOURS"] = SESSION_TIMEOUT_HOURS

# ---------------------------------------------------------------------------
# Load card data
# ---------------------------------------------------------------------------
CARDS_DIR = os.path.join(os.path.dirname(__file__), "cards")


def load_cards(cards_dir: str) -> dict:
    """Load all *.yaml files and organize into a nested module → topic → cards structure.
    
    Returns a dict like: {"Ensemble Learning": {"Random Forest": [card1, card2], ...}, ...}
    Each card has 'module' added to it for tracking.
    """
    if not os.path.isdir(cards_dir):
        sys.exit(f"ERROR: cards directory not found at {cards_dir}")
    paths = sorted(glob.glob(os.path.join(cards_dir, "*.yaml")))
    if not paths:
        sys.exit(f"ERROR: no .yaml files found in {cards_dir}")
    
    modules: dict = {}
    for path in paths:
        # Extract module name from filename: "ensemble-learning.yaml" → "Ensemble Learning"
        filename = os.path.basename(path)
        module_name = filename.replace(".yaml", "").replace("-", " ").title()
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            sys.exit(f"ERROR: {path} contains invalid YAML:\n{exc}")
        if not isinstance(data, dict):
            sys.exit(f"ERROR: {path} must be a mapping of topic keys to card lists.")
        
        # Ignore the YAML top-level key, organize by card's 'topic' field instead
        topics_dict: dict = {}
        for _, cards_list in data.items():
            for card in cards_list:
                card["module"] = module_name  # Add module to each card
                topic = card.get("topic", "General")
                if topic not in topics_dict:
                    topics_dict[topic] = []
                topics_dict[topic].append(card)
        
        modules[module_name] = topics_dict
    
    if not modules:
        sys.exit("ERROR: no cards loaded from cards directory.")
    return modules


CARDS: dict = load_cards(CARDS_DIR)

# ---------------------------------------------------------------------------
# Session weighting helpers
# ---------------------------------------------------------------------------
MIN_WEIGHT = 0.05


def card_id(card: dict) -> str:
    """Return a stable string identifier for a card."""
    return f"{card['module']}::{card['topic']}::{card['title']}"


def _check_and_refresh_session() -> None:
    """Reset weights if the session has been inactive for SESSION_TIMEOUT_HOURS.
    Always updates the last_active timestamp.
    Uses sparse storage: only cards that have been answered are stored in weights."""
    now = datetime.now(timezone.utc)
    last_active_str = session.get("last_active")
    timeout_hours = app.config["SESSION_TIMEOUT_HOURS"]

    if last_active_str:
        last_active = datetime.fromisoformat(last_active_str)
        elapsed_hours = (now - last_active).total_seconds() / 3600
        if elapsed_hours >= timeout_hours:
            session["weights"] = {}

    if "weights" not in session:
        session["weights"] = {}

    session["last_active"] = now.isoformat()


def pick_weighted_card(module_topic_keys: list) -> dict | None:
    """Select a card from the given module::topic pairs using session weights.
    Calls _check_and_refresh_session() to maintain the inactivity timer.
    
    Args:
        module_topic_keys: List of strings in format "Module Name::Topic Name"
    """
    _check_and_refresh_session()
    candidates = []
    for key in module_topic_keys:
        try:
            module, topic = key.split("::", 1)
        except ValueError:
            continue  # Skip invalid keys
        cards_list = CARDS.get(module, {}).get(topic, [])
        candidates.extend(cards_list)
    
    if not candidates:
        return None
    weights_map: dict = session["weights"]
    weights = [weights_map.get(card_id(c), 1.0) for c in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]


def halve_card_weight(cid: str) -> None:
    """Halve the session weight for the given card identifier (min MIN_WEIGHT)."""
    _check_and_refresh_session()
    weights: dict = session["weights"]
    current = weights.get(cid, 1.0)
    weights[cid] = max(current / 2, MIN_WEIGHT)
    session["weights"] = weights


def find_card_by_id(cid: str) -> dict | None:
    """Look up a card dict by its card_id string ('{module}::{topic}::{title}')."""
    try:
        module, topic, title = cid.split("::", 2)
    except ValueError:
        return None
    for c in CARDS.get(module, {}).get(topic, []):
        if c["title"] == title:
            return c
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    # Pass the nested structure: {module: {topic: [cards]}}
    return render_template("home.html", modules=CARDS)


@app.route("/start", methods=["POST"])
def start():
    selected_modules = request.form.getlist("modules")
    # Expand selected modules into all their module::topic pairs
    valid_selections = []
    for module in selected_modules:
        if module in CARDS:
            for topic in CARDS[module]:
                valid_selections.append(f"{module}::{topic}")
    
    if not valid_selections:
        return render_template("home.html", modules=CARDS), 400
    
    session["selected_topics"] = valid_selections
    return redirect(url_for("card"))


@app.route("/card")
def card():
    selected_topics = session.get("selected_topics")
    if not selected_topics:
        return redirect(url_for("index"))

    cid = session.get("current_card_id")
    current = find_card_by_id(cid) if cid else None
    if current is None:
        current = pick_weighted_card(selected_topics)
        if current is None:
            return redirect(url_for("index"))
        session["current_card_id"] = card_id(current)

    answer_html = Markup(md.markdown(current["answer"], extensions=["fenced_code", "tables"]))
    return render_template("card.html", card=current, answer_html=answer_html)


@app.route("/next", methods=["POST"])
def next_card():
    selected_topics = session.get("selected_topics")
    if not selected_topics:
        return redirect(url_for("index"))

    cid = request.form.get("card_id", "")
    if cid:
        halve_card_weight(cid)

    next_c = pick_weighted_card(selected_topics)
    if next_c is None:
        return redirect(url_for("index"))
    session["current_card_id"] = card_id(next_c)
    return redirect(url_for("card"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

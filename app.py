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
CARDS_YAML_PATH = os.path.join(os.path.dirname(__file__), "cards.yaml")


def load_cards(path: str) -> dict:
    """Load and validate cards.yaml. Exits with a clear error on failure."""
    if not os.path.exists(path):
        sys.exit(f"ERROR: cards.yaml not found at {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        sys.exit(f"ERROR: cards.yaml contains invalid YAML:\n{exc}")
    if not isinstance(data, dict) or not data:
        sys.exit("ERROR: cards.yaml must be a non-empty mapping of topic keys to card lists.")
    return data


CARDS: dict = load_cards(CARDS_YAML_PATH)

# ---------------------------------------------------------------------------
# Session weighting helpers
# ---------------------------------------------------------------------------
MIN_WEIGHT = 0.05


def card_id(card: dict) -> str:
    """Return a stable string identifier for a card."""
    return f"{card['topic']}::{card['title']}"


def _default_weights() -> dict:
    """Return a weights dict with every card set to 1.0."""
    return {
        card_id(card): 1.0
        for cards in CARDS.values()
        for card in cards
    }


def _check_and_refresh_session() -> None:
    """Reset weights if the session has been inactive for SESSION_TIMEOUT_HOURS.
    Always updates the last_active timestamp."""
    now = datetime.now(timezone.utc)
    last_active_str = session.get("last_active")
    timeout_hours = app.config["SESSION_TIMEOUT_HOURS"]

    if last_active_str:
        last_active = datetime.fromisoformat(last_active_str)
        elapsed_hours = (now - last_active).total_seconds() / 3600
        if elapsed_hours >= timeout_hours:
            session["weights"] = _default_weights()

    if "weights" not in session:
        session["weights"] = _default_weights()

    session["last_active"] = now.isoformat()


def pick_weighted_card(topic_keys: list) -> dict | None:
    """Select a card from the given topics using session weights.
    Calls _check_and_refresh_session() to maintain the inactivity timer."""
    _check_and_refresh_session()
    candidates = [
        card
        for topic in topic_keys
        for card in CARDS.get(topic, [])
    ]
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
    """Look up a card dict by its card_id string ('{topic}::{title}')."""
    try:
        topic, title = cid.split("::", 1)
    except ValueError:
        return None
    for c in CARDS.get(topic, []):
        if c["title"] == title:
            return c
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    topics = list(CARDS.keys())
    return render_template("home.html", topics=topics)


@app.route("/start", methods=["POST"])
def start():
    selected = request.form.getlist("topics")
    valid_topics = list(CARDS.keys())
    # Sanitise: only keep topics that actually exist
    selected = [t for t in selected if t in valid_topics]
    if not selected:
        # Fall back to home — client-side validation prevents this normally
        topics = valid_topics
        return render_template("home.html", topics=topics), 400
    session["selected_topics"] = selected
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

    answer_html = Markup(md.markdown(current["answer"]))
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

# PRD: Lightweight Flashcard Study App

## 1. Introduction / Overview

A lightweight, mobile-optimised flashcard web application built with Flask to help an L7 Data Science apprentice study course material. Cards are stored in human-editable YAML files. The app presents cards semi-randomly within a session, deprioritising cards that have already been seen, so unseen cards are more likely to appear next. Session state resets after a period of inactivity. The app runs locally and is deployed to Posit Cloud.

---

## 2. Goals

- Provide a friction-free, mobile-friendly interface for studying flashcards
- Allow the user to filter by topic or study all topics at once
- Deprioritise already-seen cards within a session using a weighting system
- Support rich-text answers rendered as Markdown (formulae, code blocks, bold, italics, quotes)
- Be easy to extend by editing a plain YAML file
- Run locally and be deployable to Posit Cloud with minimal configuration

---

## 3. User Stories

### US-001: Select Topics to Study
**Description:** As a user, I want to select which topic(s) to study before starting a session, so that I can focus on a specific subject area.

**Acceptance Criteria:**
- [ ] A home/lobby screen lists all topics found in the YAML data file
- [ ] The user can select one or more topics via checkboxes
- [ ] An "All Topics" option selects all topics at once
- [ ] At least one topic must be selected before proceeding (validation shown in UI)
- [ ] A "Start Session" button launches the card view with the selected topics
- [ ] Verify in browser using dev-browser skill

---

### US-002: View the Front of a Flashcard
**Description:** As a user, I want to see the prompt on the front of a card, so that I can recall the answer before flipping.

**Acceptance Criteria:**
- [ ] The card front displays the **prompt text** centred in the middle of the card
- [ ] The **card title** is displayed in the top-left corner
- [ ] The card is visually styled to look like a physical flashcard
- [ ] The card is responsive and renders well on a mobile screen (min 375px width)
- [ ] Verify in browser using dev-browser skill

---

### US-003: Flip a Card to See the Answer
**Description:** As a user, I want to flip the card by tapping/clicking it, so that I can see the answer and check my recall.

**Acceptance Criteria:**
- [ ] Tapping/clicking the card triggers a flip animation (CSS 3D flip)
- [ ] The card back displays the **answer** rendered as Markdown (supports: KaTeX/MathJax formulae, code blocks, bold, italics, blockquotes)
- [ ] The **reference** is displayed in the bottom-right of the card back
- [ ] The flip animation is smooth (CSS transition, not a page reload)
- [ ] Verify in browser using dev-browser skill

---

### US-004: Navigate to the Next Card
**Description:** As a user, I want to move to the next card after reviewing the current one, so that I can work through my session.

**Acceptance Criteria:**
- [ ] A "Next Card" button is visible (either always, or once the card has been flipped)
- [ ] Clicking "Next Card" records that the current card has been seen and applies the negative weighting
- [ ] The next card is selected using the weighted random function (see FR-5)
- [ ] The new card is displayed face-up (front side)
- [ ] Verify in browser using dev-browser skill

---

### US-005: Semi-Random Card Ordering with Session Weighting
**Description:** As a user, I want unseen cards to appear more frequently, so that I don't keep reviewing the same cards I've already studied.

**Acceptance Criteria:**
- [ ] Unseen cards have a base weight of 1.0
- [ ] A card's weight is reduced by 50% each time it is shown (e.g., 1st view → 0.5, 2nd → 0.25)
- [ ] The minimum weight a card can reach is 0.05 (it can always reappear)
- [ ] Card selection uses a weighted random algorithm based on current weights
- [ ] Card weights are stored in server-side session state, not in the YAML file

---

### US-006: Session Reset After Inactivity
**Description:** As a user, I want my session weights to reset after I've been inactive, so that I start fresh on a new study session.

**Acceptance Criteria:**
- [ ] Session weights reset automatically after **4 hours of inactivity** (configurable via a constant in the app config)
- [ ] The inactivity timer resets on every card interaction
- [ ] After reset, all card weights return to 1.0
- [ ] The user is not shown an error or interruption; the reset is silent (they simply get a fresh session)

---

### US-007: Edit Cards via YAML
**Description:** As a user, I want to add or edit flashcards by editing a YAML file, so that I can maintain my card deck without touching application code.

**Acceptance Criteria:**
- [ ] The YAML file supports multiple top-level topic keys, each containing a list of cards
- [ ] Each card has four fields: `title`, `prompt`, `answer`, `reference`
- [ ] The app loads the YAML file on startup (and reloads on Posit Cloud redeploy)
- [ ] A sample YAML file with at least two topics and two cards each is provided
- [ ] An invalid YAML file causes a clear error message on startup, not a silent failure

---

## 4. Functional Requirements

- **FR-1:** The app must be built using **Flask** and **Jinja2** templates.
- **FR-2:** Card data must be stored in a single **YAML file** (`cards.yaml`) in a defined schema (see US-007).
- **FR-3:** The home screen must list all topics from the YAML file and allow multi-select filtering, including an "All Topics" shortcut.
- **FR-4:** The card UI must display: front (title top-left, prompt centre) and back (answer centre as rendered Markdown, reference bottom-right).
- **FR-5:** Card weights must be tracked in the Flask server-side session. Each time a card is shown, its weight is halved (minimum 0.05). Weighted random selection uses `random.choices()` with the `weights` parameter.
- **FR-6:** Session weights must reset after **4 hours of inactivity**, controlled by a `SESSION_TIMEOUT_HOURS` constant.
- **FR-7:** Markdown in answers must be rendered server-side using the `markdown` Python library (with MathJax loaded client-side for LaTeX formulae).
- **FR-8:** The card flip must be implemented as a **CSS 3D transform** triggered by a JavaScript click event — no page reload.
- **FR-9:** The app must be **mobile-responsive**, using a viewport meta tag and flexible CSS (no fixed-pixel widths).
- **FR-10:** The app must be deployable to **Posit Cloud** and include a `requirements.txt` and any necessary configuration files (e.g., `app.py` as the entry point).
- **FR-11:** A `.env.example` or config constant must expose `SESSION_TIMEOUT_HOURS` and `SECRET_KEY` for easy configuration.

---

## 5. Non-Goals (Out of Scope)

- No user accounts or login — single-user app only
- No persistent scoring or long-term progress tracking across sessions
- No ability to add/delete cards from within the app UI — editing is done directly in the YAML file
- No audio, images, or video in cards
- No spaced repetition algorithm (e.g., SM-2) — simple in-session weighting only
- No card editor or admin panel

---

## 6. Design Considerations

- **Mobile-first layout:** The card should take up most of the viewport on a phone screen. Use a max-width container (e.g., 480px) centred on desktop.
- **Card styling:** Rounded corners, subtle shadow, clear front/back visual distinction (e.g., different background colour on flip).
- **Typography:** Use a clean sans-serif font. Answer Markdown should use consistent heading/code styles.
- **Navigation:** Keep controls minimal — "Next Card" button and a topic indicator (e.g., "Topic: Intro to ML") are sufficient.
- **Flip animation:** Use CSS `perspective` and `rotateY` so the card appears to physically turn over.

---

## 7. Technical Considerations

- **Framework:** Flask (Python), Jinja2 templates, vanilla CSS + JS (no frontend framework needed)
- **Markdown rendering:** `markdown` Python package (server-side), MathJax CDN (client-side for LaTeX)
- **Session storage:** Flask's built-in `session` (cookie-based), which requires a `SECRET_KEY`
- **YAML parsing:** `PyYAML` (`pyyaml` package)
- **Posit Cloud deployment:** Posit Cloud supports Shiny and Flask apps; requires a `requirements.txt` and `app.py` entry point. The app should bind to `host="0.0.0.0"` and read `PORT` from env if available.
- **Dependencies (approximate):** `flask`, `pyyaml`, `markdown`, `python-dotenv`

---

## 8. Success Metrics

- All flashcards in `cards.yaml` are accessible and render correctly in browser
- Flipping a card shows correctly rendered Markdown including at least one LaTeX formula
- After 5 interactions, previously-seen cards appear less frequently than unseen cards (verifiable by inspecting session weights)
- App loads and functions correctly on a mobile browser at 375px width
- App deploys and runs successfully on Posit Cloud

---

## 9. Open Questions

- **Session timeout value:** Defaulting to 4 hours — confirm this is appropriate or adjust `SESSION_TIMEOUT_HOURS`.
- **YAML migration:** The existing `note-cards.json` will need to be converted to YAML format — should a migration script be included?
- **MathJax vs KaTeX:** MathJax is easier to integrate but slower; KaTeX is faster but has less coverage. Default will be MathJax — flag if formulae don't render.
- **Posit Cloud tier:** Free tier has sleep/idle limits; the silent session reset approach is compatible with this.

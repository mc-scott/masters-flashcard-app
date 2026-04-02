# Flashcard Study App

A lightweight, mobile-optimised flashcard web app built with Flask for studying L7 Data Science apprenticeship material. Cards are stored in a human-editable YAML file and presented semi-randomly, deprioritising cards already seen within a session.

## Features

- **Topic filtering** — select one or more topics (or all) on the home screen before starting a session
- **Weighted card selection** — unseen cards appear more frequently; each time a card is shown its weight is halved (minimum 0.05)
- **Card flip animation** — CSS 3D flip reveals the answer without a page reload
- **Markdown answers** — answers render as Markdown server-side, with MathJax for LaTeX formulae
- **Session reset** — weights automatically reset after 4 hours of inactivity
- **Mobile-first** — responsive layout optimised for 375px+ screens

## Project Structure

```
00-flash-card-app/
├── app.py            # Flask application
├── cards.yaml        # Card data (edit this to add/update cards)
├── requirements.txt  # Pip dependencies
├── pyproject.toml    # Project metadata
└── templates/        # Jinja2 HTML templates
```

## Getting Started

### Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

```bash
# Create and activate a virtual environment
uv venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
uv pip install -r requirements.txt
```

### Running Locally

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

### Configuration

| Variable               | Default                        | Description                          |
|------------------------|--------------------------------|--------------------------------------|
| `SECRET_KEY`           | `dev-secret-change-in-production` | Flask session secret key          |
| `SESSION_TIMEOUT_HOURS`| `4`                            | Hours of inactivity before session resets |
| `PORT`                 | `5000`                         | Port the app listens on              |

Set `SECRET_KEY` via an environment variable in production:

```bash
SECRET_KEY=your-secret-here python app.py
```

## Card Format

Cards are defined in `cards.yaml`. Each top-level key is a topic, containing a list of cards:

```yaml
Topic Name:
  - topic: Topic Name
    title: Card Title
    prompt: The question shown on the front of the card.
    answer: |
      The answer shown on the back, rendered as **Markdown**.

      Supports LaTeX: $y = f(\boldsymbol{x})$

      And code blocks:
      ```python
      print("hello")
      ```
    reference: source-notebook.ipynb
```

## Deployment (Posit Cloud)

1. Upload the project files to Posit Cloud.
2. Set the `SECRET_KEY` environment variable.
3. Posit Cloud will serve `app.py` as the entry point. The app binds to `host="0.0.0.0"` and reads `PORT` from the environment automatically.

## Dependencies

| Package        | Purpose                          |
|----------------|----------------------------------|
| `flask`        | Web framework                    |
| `pyyaml`       | YAML parsing for `cards.yaml`    |
| `markdown`     | Server-side Markdown rendering   |
| `python-dotenv`| Loading environment variables    |

## Using a github skill to create flashcards

1. Run notebooks_to_markdown.py in the root. E.g. `python notebooks_to_markdown.py "c:\Users\ScottM\code_dev\L7 Apprenticeship\05-ensemble-learning"`
  - This converts all .ipynb files to markdown and saves them to a folder under your specified folder called notes
  - This ensures easier reading by the copilot skills
1. In chat, call the create-flashcards skill using `/create-flashcards 05-ensemble-learning`
  - This will append small, self-contained learnings to cards.yaml, adding them to the app.
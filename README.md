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

## Deployment (PythonAnywhere)

1. **Connect to your private GitHub repo** — generate a personal access token on GitHub (Settings → Developer settings → Personal access tokens), then clone using:
   ```bash
   git clone https://<your-token>@github.com/<your-username>/<your-repo>.git
   ```
2. Upload the project files to PythonAnywhere (via Git clone or the Files tab).
2. In the **Web** tab, create a new web app and select **Manual configuration** with the appropriate Python version.
3. Set the **Source code** directory and **Working directory** to your project folder.
4. In the **WSGI configuration file**, replace the default content with:
   ```python
   import sys
   sys.path.insert(0, '/home/<your-username>/<your-project-folder>')
   from app import app as application
   ```
5. In the **Web** tab under **Environment variables**, set `SECRET_KEY` to a strong secret value.
6. Open a **Bash console** and install dependencies:
   ```bash
   pip install --user flask pyyaml markdown python-dotenv
   ```
7. Click **Reload** in the Web tab to apply changes.

### Updating the app

1. Log in: PythonAnywhere.com/user/...
2. Open the built-in bash terminal
3. `ls` to refresh on folder structure then `cd` into correct folder
4. `git status` to check git configured correctly then `git pull origin master`
5. Click **Reload** in the Web tab to apply changes.

## Dependencies

| Package        | Purpose                          |
|----------------|----------------------------------|
| `flask`        | Web framework                    |
| `pyyaml`       | YAML parsing for `cards.yaml`    |
| `markdown`     | Server-side Markdown rendering   |
| `python-dotenv`| Loading environment variables    |

## Using a github skill to create flashcards

1. Run ipynb_to_md.py in the root. E.g. `python ipynb_to_md.py "05-ensemble-learning"`
  - This converts all .ipynb files to markdown and saves them to a sub-folder under your specified folder called notes
  - This ensures easier reading by the copilot skills
  - Clesanse large images from md files to avoid burning tokens
1. In chat, call the create-flashcards skill using `/create-flashcards 05-ensemble-learning`
  - This will append small, self-contained learnings to the modules yaml file in `cards/`, adding them to the app.
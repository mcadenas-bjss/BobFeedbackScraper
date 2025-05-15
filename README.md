# Feedback Scraper

A web scraper for extracting peer feedback from HiBob performance reviews.

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install chromium
```

## Usage

Run the scraper with a name argument:

```bash
python -m feedback_scraper "First Last"
```

The script will generate a markdown file with the feedback in the following format:

- Self Review
- Peer feedback from each team member
# BobFeedbackScraper

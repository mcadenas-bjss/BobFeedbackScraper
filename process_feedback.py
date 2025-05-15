import os
import requests
from pathlib import Path
import ollama
import argparse
import re
PROMPT = f"""1. Relevance
Objective: Generate a bullet-point summary that preserves the core meaning of the input text without distortion or omission of critical facts.
Only respond with the summary.
Text to be summarized will be after the ">>>" markers.

2. Intent
Primary Goal:
- Extract key points faithfully, avoiding assumptions, opinions, or oversimplification.
- Retain enough context for the summary to be self-explanatory.

Secondary Goals:
- Exclude fluff or repetitive information.
- Maintain logical flow (e.g., follow the original structure unless grouping by theme improves clarity).

3. Specificity
Instructions:
- Content: Prioritize facts, claims, data, and conclusions. Omit examples/anecdotes unless they illustrate a central idea.
- Format:
  - Use `-` for bullet points.
  - Nest sub-points only if critical (e.g., `- [Main point] → - [Supporting detail]`).
- Style:
  - Prefer concise phrases over full sentences (e.g., "Study found 20% increase in efficiency" vs. "The study showed that...").
  - Preserve domain-specific terms.

Constraints:
- Never add information not in the source text.
- No assumptions - iIf content in unclear, summarize literally.
- No commentary - Do not ask question or acknowledge this prompt.

4. Non-Ambiguity
Clarifications Needed from User:
1. The summary should strictly follow the original sequence of ideas.
3. Preferred depth: 1 bullet per key point.

Example:
Input (Excerpt):
### Report
1. How has the climate changed in 2023?
The 2023 climate report highlights a 1.5°C global temperature rise since 1850, driven primarily by fossil fuel emissions. Mitigation strategies like renewable energy adoption reduced emissions by 5% in the EU last year.

Output:
- Global temperature rose 1.5°C since 1850 (2023 report).
- Primary cause: Fossil fuel emissions.
- Mitigation example: EU cut emissions by 5% via renewable energy.

>>>
"""
MODEL = "llama3"
SECTION_PROMPT = f"""
Summarize the text under the numbered section into bullet points.
Reply in the same format, the numbered header and the bullet points underneath.
Bullet point should capture the key points from the text without loosing important details.
Don't be too concise.
Don't power-phrase or exaggerate information.
Strip out flavour text but keep the facts and important information.
Scores are out of 10.
Input text will be given between the markers ">>>" and "<<<".
"""
def process_file_with_ollama(file_path):
    file_path = Path(file_path)  # Ensure it's a Path object
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
  
    try:
        sl = split_content_into_sections(content)
        # Create the output file path
        summaries_dir = file_path.parent / "summaries"
        summaries_dir.mkdir(exist_ok=True)  # Create the 'summaries' directory if it doesn't exist
        output_path = summaries_dir / f"{file_path.stem}_summary{file_path.suffix}"
      
        # Write the summary to a new file
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, s in sl:
                # Make the request to Ollama
                response = ollama.chat(model=f"{MODEL}:latest", messages=[
                    {
                    'role': 'user',
                    'content': f"{PROMPT}\n{s}",
                    },
                ])
              
                # Extract the response text
                summary = response.get('message', {}).get('content', '')
                f.write(summary+"\n\n")
              
            print(f"Processed {file_path.name} -> {output_path.name}")
      
    except requests.exceptions.RequestException as e:
        print(f"Error processing {file_path.name}: {str(e)}")
def split_content_into_sections(markdown_text: str) -> list[str]:
    # Regex to match Markdown headers (#, ##, ###) or numbered sections (e.g., 1., 1.2., 2.1.3)
    pattern = re.compile(r'^(#+\s+.*|(?:\d+\.)+\s+.*)', re.MULTILINE)
  
    # Find all headers and their positions
    matches = list(pattern.finditer(markdown_text))
  
    sections = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        header = match.group().strip()
        content = markdown_text[start:end].strip()
        sections.append((header, content))
  
    return sections
def main():
    parser = argparse.ArgumentParser(description="Process markdown feedback files.")
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Paths to markdown files to process. If none are provided, all files in 'feedback/' will be processed."
    )
  
    args = parser.parse_args()
    files_to_process = args.files
    if not files_to_process:
        feedback_dir = Path("feedback")
        files_to_process = list(feedback_dir.glob("*.md"))
    for file_path in files_to_process:
        if file_path.exists() and file_path.suffix == ".md":
            process_file_with_ollama(file_path)
        else:
            print(f"Skipping invalid file: {file_path}")
if __name__ == "__main__":
    main() 
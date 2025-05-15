from playwright.sync_api import sync_playwright, TimeoutError
import time
from datetime import datetime
import argparse
import sys
import os
user_dir = '/tmp/playwright'

if not os.path.exists(user_dir):
  os.makedirs(user_dir)

NEW_LINE = '\n\n'

def scrape_feedback(name):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_dir, headless=False)
        # context = browser.new_context()
        page = browser.new_page()
        page.set_default_timeout(60000)  # Set default timeout to 60 seconds

        try:
            # Navigate to the reviews page
            page.goto('https://app.hibob.com/performance/my-reviews/tabs/manager', timeout=60000)
            
            # Wait for login if needed
            if page.url.startswith('https://app.hibob.com/login'):
                print("Please log in to HiBob and press Enter when ready...")
                input()

            # Wait for the grid to load
            try:
                page.wait_for_selector('ag-grid-angular', timeout=60000)
            except TimeoutError:
                print("Timeout waiting for the grid to load. Please check if you're properly logged in.")
                return

            # Find and click the current month's section
            current_month = datetime.now().strftime('%B')
            sections = page.query_selector_all('section')
            found_section = False

            target_row = None
            
            print(f"found {len(sections)} sections")
            for section in sections:
                # Check if section is expanded, if not click it
                if section.get_attribute('data-expanded') != 'true':
                    section.click()
                    time.sleep(5)
                
                header = section.query_selector('header')
                if header:
                    header_text = header.inner_text()
                    print(f"Looking for {current_month} in {header_text}")
                    # Match if the header contains the current month (e.g., "April 2025 Six Month Review")
                    if current_month in header_text:
                        # found_section = True
                        print(f"Found section: {header_text}")
                        # Wait a moment for the section to expand
                        page.wait_for_selector('div[role="row"]', timeout=50000)
                        rows = page.query_selector_all('div[role="row"]')
                        for row in rows:
                            employee_cell = row.query_selector('div[col-id="employee"]')
                            if employee_cell and name.lower() in employee_cell.inner_text().lower():
                                target_row = row
                                found_section = True
                                break
                        if found_section:
                            break

            if not found_section:
                print(f"Could not find section for current month ({current_month})")
                return

            if not target_row:
                print(f"Could not find feedback for {name}")
                return

            # Click the peer button to reveal the View button
            peer_button = target_row.query_selector('div[col-id="peer"] button')
            peer_button.click()

            # Wait for and click the View button
            try:
                page.wait_for_selector('#menu__view__btn', timeout=60000)
                page.click('#menu__view__btn')
            except TimeoutError:
                print("Timeout waiting for the View button to appear")
                return

            # Wait for the reviews menu
            try:
                page.wait_for_selector('h4:text("Reviewers")', timeout=60000)
            except TimeoutError:
                print("Timeout waiting for the Reviews menu to appear")
                return

            # Get all review items
            reviews = page.query_selector_all('ul > li')
            
            # Create the markdown file and write the header
            feedback_dir = "feedback"
            if not os.path.exists(feedback_dir):
                os.makedirs(feedback_dir)
                
            filename = os.path.join(feedback_dir, f"{name.replace(' ', '_')}_feedback.md")
            with open(filename, 'w') as f:
                f.write(f"# {name} Review\n\n")
                f.write("## Self Review\n")
            
            print(f"Found {len(reviews)} reviews")
            self_review_written = False
            peer_feedback_section_written = False
            
            for i, review in enumerate(reviews):
                print(f"Processing {review.inner_text()}'s review")
                # Skip manager review (second item)
                if i == 1:
                    continue

                review.click()
                try:
                    page.wait_for_selector('b-presenter-container-item', timeout=6000)
                except TimeoutError:
                    print(f"Timeout waiting for review content to load (review {i+1})")
                    continue

                reviewer_name = review.query_selector('h6').inner_text()
                feedback_items = page.query_selector_all('b-presenter-container-item > div > b-presenter-item')
                print(f"Found {len(feedback_items)} feedback items")
                feedback_text = []
                for j, question in enumerate(feedback_items):
                    print(f"getting question {j}")
                    q = question.query_selector('header > b-form-base-item-view > div > div').inner_text()
                    f = question.query_selector('b-presenter-item-wrapper').inner_text().replace("Read more...", "")
                    print(f"{f}")
                    feedback_text.append("".join([f"{j+1}. {q}" , NEW_LINE, f]))

                self_score: str
                if name in reviewer_name:
                    print("getting score")
                    self_score = page.query_selector('button.bg-select-yellow').inner_text()

                # Write to the markdown file incrementally
                with open(filename, 'a') as f:
                    if "Self" in review.inner_text():
                        feedback_text.pop(0)
                        f.write("\n1. Score\n\n" + self_score + NEW_LINE + NEW_LINE.join(feedback_text) + NEW_LINE)
                        self_review_written = True
                    else:
                        # Write the Peer Feedback section header if not already written
                        if not peer_feedback_section_written and self_review_written:
                            f.write("## Peer Feedback\n\n")
                            peer_feedback_section_written = True
                        
                        f.write(f"### {reviewer_name}\n\n")
                        f.write(NEW_LINE.join(feedback_text) + "\n\n")
                
                print(f"Wrote {reviewer_name}'s feedback to {filename}")

            print(f"Feedback has been saved to {filename}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser(description='Scrape peer feedback from HiBob')
    parser.add_argument('name', help='Name of the person to search for (e.g., "First Last")')
    args = parser.parse_args()

    scrape_feedback(args.name)

if __name__ == "__main__":
    main() 
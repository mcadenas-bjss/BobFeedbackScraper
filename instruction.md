# Project Overview

Scraping bot for squad members peer feedback.
The scraper needs to look for all feedback received by an individual as well as the persons self review which is located in the same place.
The scraper will take a name as an argument which will be used as the search criteria. Name is a combination of first and last e.g. "Mauricio Cadenas" as should be matched case insensitive.
Create a markdown document containing the self review of the individual plus all the feedback received.
The structure should be a well formatted document with the header e.g.

# "Mauricio Cadenas Review"

## Self Review

Self review...

## Peer feedback

### <feedback givers name>

Peer feedback...

---

## Technical project details

The web scraper will be written in python.
A virtual environment should be created for managing dependencies.
requirements.txt should be created to maintain dependencies and versions required.
The web crawling library we are using is Scrapy (pip install Scrapy) for python with a playwrite plugin (pip install scrapy-playwright).
Playwrite will run in a chromium browser.

## Webpage details

Starting page: https://app.hibob.com/performance/my-reviews/tabs/manager

1. Open all section elements that have a header starting with current month e.g. April. Each section contains a ag-grid-angular element where each row after the first would be a squad member.
2. Find the row with the search name in each row (row-id 0 onwards) column 1 (col-id="employee").
3. Find the button in col-id="peer" to reveal the "View" button id="menu\_\_view\_\_btn". Click this button to navigate to all feedback for the individual.
4. Find the side menu with an h4 "Reviews" and loop though the ul under it.
   Each li is a separate review. Starting with the self review from the individual (label it as such).
   The second li is the manager review which can be skipped.
   Collect all reviews labeled by the name of the feedback giver.
5. Clicking on the li will update the main view to show that persons feedback.
6. Get all <header><b-presenter-item-wrapper> combinations and add them to the markdown document.

## Instructions

Create the web scraper as described above to the point where it can reach the buy ticket page.

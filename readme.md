CLI Syntax: `python component_scraper.py <csv file> <component class name>`

Script to compare `<div>` component heading sizes to previous "structural" headings in the DOM.

Outputs a CSV file in the current working directory.
Input CSV must have one column of URLs to scrape with the header "url".
Output CSV has a column of URLs and titles of component headings that triggered the condition.

Previous "structural" headings are defined as children of a `<section>` or element with class "block-richtext" that occur sequentially before the given component heading.

Current condition is a component heading being larger than the previous "structural" heading.

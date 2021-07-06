CLI Syntax: `python component_scraper.py <csv file> <component class name>`

Script to compare <div> component heading sizes to previous "structural" headings in the DOM.
Outputs a csv file in the current working directory.

Input file is a text file with a URL path on each line.
Output CSV has a column of URLs and titles of component headings that triggered the condition.

Previous "structural" headings are defined as children of a <section> tag or tag with class "block-richtext", that occur sequentially prior to the given component heading tag.

Current condition is a component heading being larger than the previous "structural" heading.

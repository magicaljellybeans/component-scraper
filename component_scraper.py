#!/usr/bin/env python
"""
CLI Syntax: python component_scraper.py <csv file> <component class name>

Script to compare <div> component heading sizes to previous "structural" 
headings in the DOM.
Outputs a csv file in the current working directory.

Input file is a text file with a URL path on each line.
Output CSV has a column of URLs and titles of component headings that 
triggered the condition.

Previous "structural" headings are defined as children of a <section> 
tag or tag with class "block-richtext", that occur sequentially prior 
to the given component heading tag.

Current condition is a component heading being larger than the 
previous "structural" heading.

"""
import requests
import csv
import re
import sys

from bs4 import BeautifulSoup


heading_tags = re.compile("^h[1-6]$")


def read_urls_from_file(file):
    with open(file, mode="r") as file:
        for line in file:
            if "/nhsuk/" in line:
                yield line.replace("/nhsuk", "https://www.nhs.uk").strip()


def look_for_headers(file, component):
    """Check page for headers meeting condition"""
    bad_urls = []
    counter = 0

    for index, url in enumerate(read_urls_from_file(file)):
        try:
            html = requests.get(url).text
        except requests.exceptions.RequestException:
            bad_urls.append(url)

        soup = BeautifulSoup(html, "html.parser")

        print(f"Scraping page {index + 1} ... {url}")

        components = soup.find_all("div", class_=f"{component}")

        for target_component in components:
            target_component_heading = target_component.find(heading_tags)

            if target_component_heading is None:
                continue

            target_heading_size = target_component_heading.name[1]

            prior_heading = find_prior_structural_heading(
                target_component_heading.find_previous(heading_tags)
            )

            if prior_heading is None:
                continue

            prior_heading_size = prior_heading.name[1]

            if target_heading_size < prior_heading_size:
                title = target_component_heading.text.strip()
                counter += 1
                print(f"    Incorrect sizing on {title}")
                yield url, title

    for url in bad_urls:
        print(f"Bad URL: {url}")

    print(f"Pages with issues: {counter}")


def find_prior_structural_heading(heading):
    if heading is None:
        return None
    if heading.parent.name == "section":
        return heading
    try:
        if "block-richtext" in heading.parent["class"]:
            return heading
    except KeyError:
        # Some tags don't have the "class" attr and can throw KeyError
        pass

    find_prior_structural_heading(heading.find_previous(heading_tags))


def write_to_csv(file, component):
    with open(f"{component}_issue-list.csv", mode="w") as new_file:
        writer = csv.writer(new_file, delimiter=",")

        for url, header in look_for_headers(file, component):
            writer.writerow([url, header])


if __name__ == "__main__":
    file = sys.argv[1]
    component = sys.argv[2]

    write_to_csv(file, component)

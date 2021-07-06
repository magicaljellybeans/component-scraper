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


def look_for_issues(file, component_type):
    """Compend dict of faulty headers and urls they occur on"""
    faulty_headers = {}
    bad_urls = []

    for index, url in enumerate(read_urls_from_file(file)):
        try:
            html = requests.get(url).text
        except requests.exceptions.RequestException:
            bad_urls.append(url)

        soup = BeautifulSoup(html, "html.parser")

        print(f"Scraping page {index + 1} ... {url}")

        components = soup.find_all("div", class_=f"{component_type}")

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

                print(f"    Incorrect sizing on {title}")

                if url in faulty_headers:
                    faulty_headers[url].append(title)
                else:
                    faulty_headers[url] = [title]

    for url in bad_urls:
        print(f"Bad URL: {url}")

    print(f"Pages with issues: {len(faulty_headers.keys())}")

    return faulty_headers


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


def write_to_csv(faulty_headers, component):
    with open(f"{component}_issue-list.csv", mode="w") as new_file:
        writer = csv.writer(new_file, delimiter=",")

        for url in faulty_headers:
            for header in faulty_headers[url]:
                writer.writerow([url, header])


if __name__ == "__main__":
    file = sys.argv[1]
    component = sys.argv[2]

    faulty_headers = look_for_issues(file, component)
    write_to_csv(faulty_headers, component)

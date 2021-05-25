#!/usr/bin/env python
import requests
import csv
import re
import sys

from bs4 import BeautifulSoup


heading_tags = re.compile("^h[1-6]$")


def get_from_csv(file):
    with open(file, mode="r") as csv_file:

        url_list = []
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            url = row["url"].replace("www.", r"https://")
            url_list.append(url)

    return url_list


def look_for_issues(url_list, component_type):

    issue_dict = {}
    len_list = len(url_list)
    bad_urls = []

    for index, url in enumerate(url_list):

        try:
            html = requests.get(url).text
        except requests.exceptions.RequestException:
            bad_urls.append(url)

        soup = BeautifulSoup(html, "html.parser")

        print(f"Scraping page {index + 1} of {len_list}")

        components = soup.find_all("div", class_=f"{component_type}")

        for component in components:
            component_heading = component.find(heading_tags)

            if component_heading is None:
                continue

            component_heading_size = component_heading.name[1]

            previous_heading = find_previous_structural_heading(
                component_heading.find_previous(heading_tags)
            )

            if previous_heading is None:
                continue

            previous_heading_size = previous_heading.name[1]

            if component_heading_size <= previous_heading_size:
                title = component_heading.text.strip()

                print(f"    Incorrect sizing on {title}")

                if url in issue_dict:
                    issue_dict[url].append(title)
                else:
                    issue_dict[url] = [title]

    for url in bad_urls:
        print(f"Bad URL: {url}")

    print(f"Pages with issues: {len(issue_dict.keys())}")

    return issue_dict, component_type


def find_previous_structural_heading(heading):
    if heading is None:
        return None
    if heading.parent.name == "section" or "block-richtext" in heading.parent["class"]:
        return heading

    find_previous_structural_heading(heading.find_previous(heading_tags))


def write_to_csv(input):
    issue_dict, component = input

    with open(f"{component}_issue-list.csv", mode="w") as new_file:
        writer = csv.writer(new_file, delimiter=",")

        for url in issue_dict:
            writer.writerow([url, issue_dict[url]])


if __name__ == "__main__":
    file = sys.argv[1]
    component_type = sys.argv[2]

    url_list = get_from_csv(file)
    input = look_for_issues(url_list, component_type)
    write_to_csv(input)

import requests
import csv
import pprint
import re

from bs4 import BeautifulSoup


def get_from_csv(file):
    with open(file, mode='r') as csv_file:

        url_list = []
        csv_reader = csv.DictReader(csv_file, fieldnames=['title', 'url', 'count'])

        for row in csv_reader:
            url = row['url'].replace("/nhsuk", "https://nhs.uk")
            url_list.append(url)

    return url_list

def look_for_issues(url_list, component_type):

    pp = pprint.PrettyPrinter()
    heading_tags = re.compile('^h[1-6]$')
    issue_dict = {}
    len_list = len(url_list)

    for index, url in enumerate(url_list):
        
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        print(f"Scraping page {index + 1} of {len_list}")

        components = soup.find_all("div", class_=f"{component_type}")
        
        for component in components:
            component_heading = component.find(heading_tags)
            component_heading_size = component_heading.name[1]
            previous_heading_size = component.find_previous(heading_tags).name[1]
            
            if component_heading_size <= previous_heading_size:
                title = component_heading.text.strip()

                print(f"    Incorrect sizing on {title}")

                if url in issue_dict:
                    issue_dict[url].append(title)
                else:
                    issue_dict[url] = [title]

    pp.pprint(issue_dict)
    print(f"Pages with issues: {len(issue_dict.keys())}")

    return issue_dict, component_type

def write_to_csv(input):
    issue_dict, component = input

    with open(f"{component}_issue-list.csv", mode='w') as new_file:
        writer = csv.writer(new_file, delimiter=',')

        for url in issue_dict:
            writer.writerow([url, issue_dict[url]])
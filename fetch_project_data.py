#!/usr/bin/python3


# fetches json data from source taiga project and import filter cards to
# another taiga project


from __future__ import print_function, unicode_literals
import requests
import time
import sys
import configparser
import json


def fetch_project_json(project_id, project_slug, headers):
    max_retries = 5
    while 1:
        print("getting export_id")
        r = requests.get(
            "https://api.taiga.io/api/v1/exporter/{}".format(project_id),
            headers=headers)
        if r.status_code == 429:
            sec = 45
            print(" Server overhelmed, waiting {} seconds".format(sec))
            time.sleep(sec)
            continue
        if r.status_code == 202:
            export_id = r.json()['export_id']
            break
        print(" Unknown status code {}".format(r.status_code), file=sys.stderr)
        sys.exit(1)
    retries = 0
    while 1:
        sec = 15
        print("getting the project content after {} seconds".format(sec))
        time.sleep(sec)
        r = requests.get("https://media.taiga.io/exports/{}/{}-{}.json".format(
            project_id, project_slug, export_id), headers=headers)
        if r.status_code == 404:
            retries += 1
            if max_retries <= retries:
                raise requests.ConnectTimeout
            continue
        print(r.status_code)
        return r.json()


def main():
    config = configparser.ConfigParser()
    config.read('./taiga-visibility-sync.cfg')
    token = config.get("source-project", "token")
    project_id = config.get("source-project", "project_id")
    project_slug = config.get("source-project", "project_slug")

    headers = {"Content-type": "application/json",
               "Authorization": "Bearer {}".format(token)}

    while 1:
        try:
            source_project_content = fetch_project_json(
                project_id, project_slug, headers)
            break
        except requests.ConnectionError:
            time.sleep(30)

    with open("source_project_content.json", 'w') as f:
        json.dump(source_project_content, f)

    print("source_project_content fetched")


if __name__ == '__main__':
    main()

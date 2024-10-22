import json
import sys
import requests
import argparse

def save_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_jobs(args: argparse.Namespace, page: str = "1", pages: str = "1"):
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query": f"{args.keywords} in {args.location}",
        "page": page,
        "num_pages": pages,
        "date_posted": "week",
        "actively_hiring": "true",
        }
    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    # print(response.json())
    save_json_to_file(response.json(), "jobs.json")
    if response.status_code == 200:
        jobs = response.json()["data"]
        print(f"total: {len(jobs)}", file=sys.stderr)
        for job in jobs:
            print(job['job_apply_link'])
    else:
        print("Failed to retrieve data", file=sys.stderr)
    

if __name__ == '__main__':
    args = argparse.Namespace()
    args.keywords = "android "
    args.location = "california or USA"
    get_jobs(args, "1", "3")
    get_jobs(args, "2", "3")
    get_jobs(args, "3", "3")

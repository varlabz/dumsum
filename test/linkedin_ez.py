import sys
import requests
import argparse

def get_jobs(args: argparse.Namespace):
    url = "https://linkedin-data-scraper.p.rapidapi.com/search_jobs"
    payload = {
        "keywords": args.keywords,
        "location": args.location,
        "count": args.count,
        "easy_apply": True,
        "easyApply": True
    }

    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        jobs = response.json()["response"][0]
        print(f"total: {len(jobs)}", file=sys.stderr)
        for job in jobs:
            # print(job['jobDescription'])
            print(job['jobPostingUrl'])
    else:
        print("Failed to retrieve data")
    

if __name__ == '__main__':
    args = argparse.Namespace()
    args.keywords = "android tpm"
    args.location = "san jose, ca"
    args.count = 50
    get_jobs(args)

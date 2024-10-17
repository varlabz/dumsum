# doesn't work
# has problem with geo location
import sys
import requests
import argparse

def get_jobs(args: argparse.Namespace):
    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/search-jobs"
    payload = {
        "keywords": args.keywords,
        "job_location": args.location,
        "date_posted": "Past week",
        "sort_by": "Most relevant",
        "easy_apply": "true",
        "start": 0,
    }
    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "fresh-linkedin-profile-data.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    # print(response.json())
    if response.status_code == 200:
        jobs = response.json()["data"]
        print(f"jobs total: {len(jobs)}", file=sys.stderr)
        for job in jobs:
            print(job['job_url'])
    else:
        print("Failed to retrieve data")
  
if __name__ == '__main__':
    args = argparse.Namespace()
    args.keywords = "android tpm"
    args.location = "95123 san jose, ca"
    get_jobs(args)

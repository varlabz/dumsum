import sys
import requests
import argparse

def get_location_id(location: str):
    url = "https://linkedin-data-api.p.rapidapi.com/search-locations"
    querystring = {"keyword":location}
    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    # print(response.json())
    # id:"urn:li:geo:103035651"
    # name:"Berlin, Germany"
    if response.status_code == 200:
        locations = response.json()["data"]["items"]
        print(f"location total: {len(locations)}", file=sys.stderr)
        print(f"location: {locations[0]}", file=sys.stderr)
        return locations[0]['id'].split(':')[-1]
    else:
        print("Failed to retrieve data")


def get_jobs(args: argparse.Namespace):
    locationId = get_location_id(args.location)
    url = "https://linkedin-data-api.p.rapidapi.com/search-jobs-v2"
    querystring = {
        "keywords": args.keywords,
        "locationId": locationId,
        "datePosted": "pastWeek",
        "sort": "mostRelevant",
        "jobType": "fullTime",
        }
    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "linkedin-data-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    # print(response.json())
    if response.status_code == 200:
        jobs = response.json()["data"]
        print(f"jobs total: {len(jobs)}", file=sys.stderr)
        for job in jobs:
            print(job['url'])
    else:
        print("Failed to retrieve data")
  
if __name__ == '__main__':
    args = argparse.Namespace()
    args.keywords = "android tpm"
    args.location = "95123 san jose, ca"
    get_jobs(args)
    # get_location_id("95123 san jose, ca")

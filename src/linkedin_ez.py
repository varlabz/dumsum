import requests
import argparse

url = "https://linkedin-data-scraper.p.rapidapi.com/search_jobs"

def get_parser():
    parser = argparse.ArgumentParser(description='LinkedIn EZ Scraper')
    parser.add_argument('-k', '--keywords', required=True, help='Search keywords')
    parser.add_argument('-l', '--location', required=True, help='Location')
    parser.add_argument('-c', '--count', type=int, default=10, help='Number of results to return')
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    payload = {
        "keywords": args.keywords,
        "location": args.location,
        "count": args.count
    }

    headers = {
        "x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
        "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())

if __name__ == '__main__':
    main()

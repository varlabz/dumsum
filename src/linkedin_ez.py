import requests

url = "https://linkedin-data-scraper.p.rapidapi.com/search_jobs"

payload = {
	"keywords": "Mern Stack Developer",
	"location": "California, United States",
	"count": 10
}
headers = {
	"x-rapidapi-key": "bbc832e72fmshea77f81a666eb74p107782jsn224f6a30e1a6",
	"x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())


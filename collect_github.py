import requests

SEARCH_TOPIC = "agentic ai"

url = (
    "https://api.github.com/search/repositories"
    f"?q={SEARCH_TOPIC}&sort=stars&order=desc&per_page=5"
)

print(f"Searching GitHub for: {SEARCH_TOPIC}")
print()

response = requests.get(url)

if response.status_code == 200:

    data = response.json()

    print(f"Found {data['total_count']} repositories")
    print()

    for repo in data["items"]:

        print(f"📦 {repo['full_name']}")
        print(f"⭐ Stars : {repo['stargazers_count']}")
        print(f"🔗 {repo['html_url']}")
        print()

else:

    print("GitHub API Error")
    print(response.status_code)
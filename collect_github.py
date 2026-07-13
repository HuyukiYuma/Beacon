import requests

from themes import THEMES


API_URL = "https://api.github.com/search/repositories"

scores = {}

def search_github(query: str, limit: int = 5) -> None:
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": limit,
    }

    response = requests.get(API_URL, params=params, timeout=10)

    if response.status_code != 200:
        print("GitHub API Error")
        print(f"Status code: {response.status_code}")
        print(response.text)
        return

    data = response.json()

    print(f"Searching GitHub for: {query}")
    print(f"Found {data['total_count']:,} repositories")
    print()

    for repository in data["items"]:
        if repository["full_name"] in scores:
            scores[repository["full_name"]] += 1
        else:
            scores[repository["full_name"]] = 1

        print(f"📦 {repository['full_name']}")
        print(f"⭐ Stars: {repository['stargazers_count']:,}")
        print(f"🔗 {repository['html_url']}")
        print()


theme_name = "AI Agent"
print(f"Theme: {theme_name}")
print()

for keyword in THEMES[theme_name]:
    search_github(keyword)

print("==========")
print("Hit Count")
print("==========")

for repository_name, hit_count in sorted(
    scores.items(),
    key=lambda item: item[1],
    reverse=True,
):
    print(repository_name, ":", hit_count)
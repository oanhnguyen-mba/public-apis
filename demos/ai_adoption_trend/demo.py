import requests
import pandas as pd
import plotly.express as px
import time
import os

# --- 0. Lấy token từ environment variable để bảo mật ---
# Trước khi chạy: export GITHUB_TOKEN="your_token_here"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Please set your GitHub token in environment variable GITHUB_TOKEN")

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# --- 1. Danh sách topic AI cần fetch ---
topics_to_check = [
    "machine-learning",
    "deep-learning",
    "reinforcement-learning",
    "natural-language-processing",
    "computer-vision"
]

all_repos = []

# --- 2. Fetch repo từ GitHub API ---
for topic in topics_to_check:
    print(f"Fetching topic: {topic}")
    for page in range(1, 6):  # 5 page x 50 repo = 250 repo/topic
        url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page=50&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching {topic} page {page}: {response.status_code}")
            continue
        data = response.json().get('items', [])
        for repo in data:
            all_repos.append({
                'name': repo['name'],
                'stars': repo['stargazers_count'],
                'forks': repo['forks_count'],
                'created_at': repo['created_at'][:10],
                'topic': topic
            })
        time.sleep(1)  # tránh rate limit

# --- 3. Chuyển sang DataFrame ---
df = pd.DataFrame(all_repos)
df['year'] = pd.to_datetime(df['created_at']).dt.year

# --- 4. Aggregate stars theo topic và năm ---
trend = df.groupby(['year','topic'])['stars'].sum().reset_index()

# --- 5. Vẽ chart stacked bar theo topic ---
fig = px.bar(
    trend,
    x='year',
    y='stars',
    color='topic',
    title='AI Project Stars Trend on GitHub by Topic',
    labels={'stars':'Total Stars','year':'Year','topic':'AI Topic'}
)

# --- 6. Lưu chart ra HTML ---
output_file = "ai_trend_by_topic.html"
fig.write_html(output_file)
print(f"Chart saved to {output_file}. Open in browser to view the interactive chart.")

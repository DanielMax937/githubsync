import os
import subprocess
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
load_dotenv()

TOKEN=os.environ.get('GITHUP_TOKEN')
BASE_DIR = '/Volumes/SE/git'  # The directory to cd into before cloning
PER_PAGE = 1200  # 每页最多 100 条
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'token {TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}


def get_starred_repos():
    page = 1
    starred = []

    while True:
        url = f'https://api.github.com/user/starred?per_page={PER_PAGE}&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data:
            break  # 没有更多内容了

        for repo in data:
            starred.append({
                'title': repo['full_name'],
                'repo_url': repo['html_url'],
                # 'clone_url': repo['clone_url'],
                # 'description': repo['description'],
                # 'language': repo['language'],
                # 'stargazers_count': repo['stargazers_count']
            })

        page += 1

    return starred


def fetch_trending_repos():
    url = f'https://github.com/trending'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch trending page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    repos = []

    for repo in soup.select('article.Box-row'):
        title_tag = repo.select_one('h2 a')
        title = title_tag.get_text(strip=True).replace(' / ', '/')
        repo_url = 'https://github.com' + title_tag['href']

        description_tag = repo.select_one('p')
        description = description_tag.get_text(strip=True) if description_tag else ''

        lang_tag = repo.select_one('[itemprop=programmingLanguage]')
        language = lang_tag.get_text(strip=True) if lang_tag else ''

        stars_tag = repo.select_one('a[href*="/stargazers"]')
        stars = stars_tag.get_text(strip=True).replace(',', '') if stars_tag else '0'

        forks_tag = repo.select_one('a[href*="/network/members"]')
        forks = forks_tag.get_text(strip=True).replace(',', '') if forks_tag else '0'

        repos.append({
            'title': title,
            'repo_url': repo_url,
            # 'description': description,
            # 'language': language,
            # 'stars': stars,
            # 'forks': forks
        })

    return repos


def clone_repo(repo):
    name = repo['title'].split('/')[1]
    url = repo['repo_url']
    os.makedirs(BASE_DIR, exist_ok=True)

    # Full path to clone into
    target_path = os.path.join(BASE_DIR, name)

    try:
        if os.path.exists(target_path):
            print(f"🔁 Skipped (already exists): {name}")
            return
        print(f"📥 Cloning: {name}")
        path = url.replace('https://github.com/', '').rstrip('/')
        git_url = f'git@github.com:{path}.git'
        subprocess.run(['git', 'clone', git_url, name], cwd=BASE_DIR, check=True)
        print(f"✅ Done: {name}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to clone: {name}")


# Example usage
if __name__ == "__main__":
    star_repos = get_starred_repos()
    today_current_start = []
    exist_num = 1
    print(f"🌟 {len(star_repos)} starred repos")
    for repo in star_repos:
        name = repo['title'].split('/')[1]
        target_path = os.path.join(BASE_DIR, name)
        if not os.path.exists(target_path):
            today_current_start.append(repo)
            if len(today_current_start) == 30:
                break
        else:
            exist_num += 1
    print(f"🔁 Skipped (already exists): {exist_num}")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(clone_repo, today_current_start)

    repos = fetch_trending_repos()
    print(f"🌟 {len(repos)} trending repos")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(clone_repo, repos)

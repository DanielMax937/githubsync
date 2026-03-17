import os
import subprocess
import argparse
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dotenv import load_dotenv
load_dotenv()

TOKEN=os.environ.get('GITHUP_TOKEN')
BASE_DIR = '/Volumes/SE/git'  # The directory to cd into before cloning
PER_PAGE = 1500  # 每页最多 100 条
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'token {TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}
REQUEST_TIMEOUT = (10, 30)  # (connect, read) seconds
GIT_CLONE_TIMEOUT = 20 * 60  # seconds
GIT_CLONE_ATTEMPTS = 2
SSH_COMMAND = "ssh -o ConnectTimeout=30 -o ServerAliveInterval=20 -o ServerAliveCountMax=3"


def get_starred_repos(session):
    page = 1
    starred = []

    while True:
        url = f'https://api.github.com/user/starred?per_page={PER_PAGE}&page={page}'
        response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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


def fetch_trending_repos(session):
    url = f'https://github.com/trending'
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
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


def clone_repo(repo, use_proxy=False, max_attempts=GIT_CLONE_ATTEMPTS):
    name = repo['title'].split('/')[1]
    url = repo['repo_url']
    os.makedirs(BASE_DIR, exist_ok=True)

    # Full path to clone into
    target_path = os.path.join(BASE_DIR, name)

    if os.path.exists(target_path):
        print(f"🔁 Skipped (already exists): {name}")
        return

    print(f"📥 Cloning: {name}")
    path = url.replace('https://github.com/', '').rstrip('/')
    git_url = f'git@github.com:{path}.git'

    # Prepare environment for git command
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_SSH_COMMAND"] = SSH_COMMAND
    if not use_proxy:
        # Remove proxy settings if not using proxy
        env.pop('HTTP_PROXY', None)
        env.pop('HTTPS_PROXY', None)
        env.pop('http_proxy', None)
        env.pop('https_proxy', None)

    for attempt in range(1, max_attempts + 1):
        try:
            subprocess.run(
                ['git', 'clone', git_url, name],
                cwd=BASE_DIR,
                env=env,
                check=True,
                timeout=GIT_CLONE_TIMEOUT,
            )
            print(f"✅ Done: {name}")
            return
        except subprocess.TimeoutExpired:
            print(f"⏱️ Clone timeout: {name} (attempt {attempt}/{max_attempts})")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to clone: {name} (attempt {attempt}/{max_attempts})")

    print(f"🛑 Giving up: {name}")


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clone GitHub starred and trending repositories')
    parser.add_argument('--use-proxy', action='store_true', default=False,
                        help='Use system proxy settings for both HTTP requests and git (default: False)')
    args = parser.parse_args()
    
    # Create session with proxy settings + retries
    session = requests.Session()
    session.trust_env = args.use_proxy
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    print(f"🔧 Proxy mode: {'enabled' if args.use_proxy else 'disabled'}")
    
    star_repos = get_starred_repos(session)
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
        executor.map(lambda repo: clone_repo(repo, args.use_proxy), today_current_start)

    repos = fetch_trending_repos(session)
    print(f"🌟 {len(repos)} trending repos")
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda repo: clone_repo(repo, args.use_proxy), repos)

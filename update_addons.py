import urllib.request
import json
import re
import os

REPOS = {
    'linkwarden': 'linkwarden/linkwarden',
    'netdata': 'netdata/netdata',
    'syncthing': 'syncthing/syncthing',
    'vaultwarden': 'dani-garcia/vaultwarden',
    'vikunja': 'go-vikunja/vikunja',
    'affine': 'toeverything/AFFiNE'
}

def get_latest_release(repo):
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    headers = {'User-Agent': 'Mozilla/5.0'}
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data['tag_name']
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        return None

def increment_ha_version(version_str):
    parts = version_str.split('.')
    if len(parts) == 3:
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts)
    return version_str

def update_addon(addon, repo):
    latest_tag = get_latest_release(repo)
    if not latest_tag:
        return

    latest_version = latest_tag
    # Handle version string formats for each add-on based on Dockerfile structure
    if addon in ['netdata', 'vaultwarden', 'vikunja', 'syncthing']:
        if latest_version.startswith('v'):
            latest_version = latest_version[1:]

    dockerfile_path = os.path.join(addon, 'Dockerfile')
    config_path = os.path.join(addon, 'config.yaml')

    if not os.path.exists(dockerfile_path) or not os.path.exists(config_path):
        print(f"Skipping {addon}, missing files.")
        return

    # Read Dockerfile
    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    # Find current version
    version_pattern = re.compile(f'ARG {addon.upper()}_VERSION="([^"]+)"')
    match = version_pattern.search(dockerfile_content)
    if not match:
        print(f"Could not find version ARG for {addon}")
        return

    current_version = match.group(1)

    if current_version != latest_version:
        print(f"Updating {addon}: {current_version} -> {latest_version}")

        # 1. Update Dockerfile
        new_dockerfile_content = version_pattern.sub(f'ARG {addon.upper()}_VERSION="{latest_version}"', dockerfile_content)
        with open(dockerfile_path, 'w') as f:
            f.write(new_dockerfile_content)

        # 2. Update config.yaml version
        with open(config_path, 'r') as f:
            config_content = f.read()

        config_version_pattern = re.compile(r'^version:\s*"([^"]+)"', re.MULTILINE)
        config_match = config_version_pattern.search(config_content)
        if config_match:
            ha_current_version = config_match.group(1)
            ha_new_version = increment_ha_version(ha_current_version)
            new_config_content = config_version_pattern.sub(f'version: "{ha_new_version}"', config_content)
            with open(config_path, 'w') as f:
                f.write(new_config_content)
            print(f"  - config.yaml version bumped: {ha_current_version} -> {ha_new_version}")

if __name__ == '__main__':
    for addon, repo in REPOS.items():
        update_addon(addon, repo)

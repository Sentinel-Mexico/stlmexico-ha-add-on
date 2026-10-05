import re
import urllib.request
import json
import os

def get_github_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = f'token {token}'

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['tag_name']
    except Exception as e:
        print(f"Error fetching release for {repo}: {e}")
        return None

def update_version(directory, new_version_value, version_key):
    dockerfile_path = os.path.join(directory, 'Dockerfile')
    config_path = os.path.join(directory, 'config.yaml')

    if not os.path.exists(dockerfile_path) or not os.path.exists(config_path):
        return False

    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    if f'ARG {version_key}="{new_version_value}"' in dockerfile_content:
        return False

    new_dockerfile_content = re.sub(
        f'ARG {version_key}=".*?"',
        f'ARG {version_key}="{new_version_value}"',
        dockerfile_content
    )

    with open(dockerfile_path, 'w') as f:
        f.write(new_dockerfile_content)

    with open(config_path, 'r') as f:
        config_content = f.read()

    match = re.search(r'^version: "([^"]+)"', config_content, flags=re.MULTILINE)
    if match:
        old_version = match.group(1)
        parts = old_version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        new_config_version = '.'.join(parts)

        new_config_content = re.sub(
            r'^version: "[^"]+"',
            f'version: "{new_config_version}"',
            config_content,
            count=1,
            flags=re.MULTILINE
        )
        with open(config_path, 'w') as f:
            f.write(new_config_content)

        print(f"Updated {directory} to upstream {new_version_value} and config version {new_config_version}")
        return True
    return False

updates = [
    ('vaultwarden', 'dani-garcia/vaultwarden', 'VAULTWARDEN_VERSION'),
    ('vikunja', 'go-vikunja/vikunja', 'VIKUNJA_VERSION'),
    ('linkwarden', 'linkwarden/linkwarden', 'LINKWARDEN_VERSION'),
    ('syncthing', 'syncthing/syncthing', 'SYNCTHING_VERSION'),
    ('netdata', 'netdata/netdata', 'NETDATA_VERSION'),
    ('affine', 'toeverything/AFFiNE', 'AFFINE_VERSION')
]

if __name__ == "__main__":
    for directory, repo, arg_name in updates:
        latest_tag = get_github_release(repo)
        if not latest_tag:
            continue

        with open(os.path.join(directory, 'Dockerfile'), 'r') as f:
            content = f.read()

        match = re.search(f'ARG {arg_name}="(.*?)"', content)
        if not match:
            continue

        current_val = match.group(1)

        if directory == 'netdata':
            if latest_tag.startswith('v'):
                latest_tag = latest_tag[1:]
        elif directory == 'syncthing':
            if latest_tag.startswith('v'):
                latest_tag = latest_tag[1:]
        elif directory == 'vaultwarden':
            if latest_tag.startswith('v'):
                latest_tag = latest_tag[1:]

        if current_val != latest_tag:
            update_version(directory, latest_tag, arg_name)
        else:
            print(f"{directory} is already up to date ({current_val})")

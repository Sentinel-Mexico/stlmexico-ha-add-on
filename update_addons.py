import os
import re
import urllib.request
import json

ADDONS = {
    "vaultwarden": {
        "repo": "dani-garcia/vaultwarden",
        "arg_name": "VAULTWARDEN_VERSION",
        "remove_v": True
    },
    "vikunja": {
        "repo": "go-vikunja/vikunja",
        "arg_name": "VIKUNJA_VERSION",
        "remove_v": True
    },
    "linkwarden": {
        "repo": "linkwarden/linkwarden",
        "arg_name": "LINKWARDEN_VERSION",
        "remove_v": False
    },
    "syncthing": {
        "repo": "syncthing/syncthing",
        "arg_name": "SYNCTHING_VERSION",
        "remove_v": True
    },
    "netdata": {
        "repo": "netdata/netdata",
        "arg_name": "NETDATA_VERSION",
        "remove_v": True
    }
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}

    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get('tag_name')
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        return None

def bump_version(version_str):
    parts = version_str.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)

def update_addon(addon, info):
    print(f"Checking {addon}...")
    latest_tag = get_latest_release(info['repo'])
    if not latest_tag:
        return

    latest_version = latest_tag
    if info.get('remove_v') and latest_version.startswith('v'):
        latest_version = latest_version[1:]

    dockerfile_path = f"{addon}/Dockerfile"
    config_path = f"{addon}/config.yaml"

    if not os.path.exists(dockerfile_path) or not os.path.exists(config_path):
        return

    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    arg_name = info['arg_name']
    match = re.search(f'ARG {arg_name}="(.*?)"', dockerfile_content)
    if not match:
        return
    current_version = match.group(1)

    if current_version != latest_version:
        print(f"  -> Updating {addon} from {current_version} to {latest_version}")
        new_dockerfile = re.sub(f'ARG {arg_name}=".*?"', f'ARG {arg_name}="{latest_version}"', dockerfile_content)
        with open(dockerfile_path, 'w') as f:
            f.write(new_dockerfile)

        with open(config_path, 'r') as f:
            config_content = f.read()

        version_match = re.search(r'^version:\s*"(.*?)"', config_content, re.MULTILINE)
        if version_match:
            current_addon_version = version_match.group(1)
            new_addon_version = bump_version(current_addon_version)
            new_config = re.sub(r'^version:\s*".*?"', f'version: "{new_addon_version}"', config_content, flags=re.MULTILINE)
            with open(config_path, 'w') as f:
                f.write(new_config)

if __name__ == "__main__":
    for addon, info in ADDONS.items():
        update_addon(addon, info)

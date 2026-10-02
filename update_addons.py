import os
import re
import urllib.request
import json

ADDONS = {
    "vaultwarden": {
        "repo": "dani-garcia/vaultwarden",
        "dockerfile_arg": "VAULTWARDEN_VERSION",
        "has_v_prefix": False
    },
    "vikunja": {
        "repo": "go-vikunja/vikunja",
        "dockerfile_arg": "VIKUNJA_VERSION",
        "has_v_prefix": True
    },
    "linkwarden": {
        "repo": "linkwarden/linkwarden",
        "dockerfile_arg": "LINKWARDEN_VERSION",
        "has_v_prefix": True
    },
    "syncthing": {
        "repo": "syncthing/syncthing",
        "dockerfile_arg": "SYNCTHING_VERSION",
        "has_v_prefix": False # We extract v1.x.x to 1.x.x
    },
    "netdata": {
        "repo": "netdata/netdata",
        "dockerfile_arg": "NETDATA_VERSION",
        "has_v_prefix": False # Docker image uses vX.Y.Z, but we strip v in arg then add it in dockerfile
    },
    "affine": {
        "repo": "toeverything/AFFiNE",
        "dockerfile_arg": "AFFINE_VERSION",
        "has_v_prefix": False
    }
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'Bearer {github_token}'

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data['tag_name']
    except Exception as e:
        print(f"Error fetching release for {repo}: {e}")
        return None

def bump_version(current_version):
    parts = current_version.split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)
    return current_version

def update_addon(addon_dir, config):
    print(f"Checking {addon_dir}...")
    latest_tag = get_latest_release(config['repo'])
    if not latest_tag:
        return False

    dockerfile_path = os.path.join(addon_dir, 'Dockerfile')
    config_path = os.path.join(addon_dir, 'config.yaml')

    if not os.path.exists(dockerfile_path) or not os.path.exists(config_path):
        print(f"Missing files for {addon_dir}")
        return False

    # Format version string according to prefix rules
    clean_version = latest_tag
    if not config.get('has_v_prefix', False) and latest_tag.startswith('v'):
        clean_version = latest_tag[1:]

    # Read and update Dockerfile
    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    arg_pattern = f'ARG {config["dockerfile_arg"]}="([^"]+)"'
    match = re.search(arg_pattern, dockerfile_content)
    if not match:
        print(f"Could not find version arg in {dockerfile_path}")
        return False

    current_upstream_version = match.group(1)

    target_version = latest_tag if config.get('has_v_prefix', False) else clean_version

    if current_upstream_version == target_version:
        print(f"  Already up to date ({current_upstream_version})")
        return False

    print(f"  Updating {current_upstream_version} -> {target_version}")

    new_dockerfile = re.sub(arg_pattern, f'ARG {config["dockerfile_arg"]}="{target_version}"', dockerfile_content)

    with open(dockerfile_path, 'w') as f:
        f.write(new_dockerfile)

    # Read and update config.yaml
    with open(config_path, 'r') as f:
        config_data = f.read()

    version_pattern = r'version:\s*"([^"]+)"'
    match = re.search(version_pattern, config_data)
    if match:
        current_ha_version = match.group(1)
        new_ha_version = bump_version(current_ha_version)
        new_config = re.sub(version_pattern, f'version: "{new_ha_version}"', config_data)
        with open(config_path, 'w') as f:
            f.write(new_config)
        print(f"  Bumped HA version {current_ha_version} -> {new_ha_version}")

    return True

def main():
    changes = False
    for addon, config in ADDONS.items():
        if update_addon(addon, config):
            changes = True

if __name__ == "__main__":
    main()

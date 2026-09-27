import os
import re
import urllib.request
import json

addons = {
    "vaultwarden": {"repo": "dani-garcia/vaultwarden", "arg": "VAULTWARDEN_VERSION"},
    "vikunja": {"repo": "go-vikunja/vikunja", "arg": "VIKUNJA_VERSION"},
    "linkwarden": {"repo": "linkwarden/linkwarden", "arg": "LINKWARDEN_VERSION"},
    "affine": {"repo": "toeverything/AFFiNE", "arg": "AFFINE_VERSION"},
    "syncthing": {"repo": "syncthing/syncthing", "arg": "SYNCTHING_VERSION"},
    "netdata": {"repo": "netdata/netdata", "arg": "NETDATA_VERSION"},
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    if "GITHUB_TOKEN" in os.environ:
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data["tag_name"]
    except urllib.error.HTTPError as e:
        if e.code == 404: # Maybe no releases, try tags
            return get_latest_tag(repo)
        print(f"HTTP Error fetching {repo}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        return None

def get_latest_tag(repo):
    url = f"https://api.github.com/repos/{repo}/tags"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    if "GITHUB_TOKEN" in os.environ:
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if len(data) > 0:
                return data[0]["name"]
            return None
    except Exception as e:
        print(f"Error fetching tags for {repo}: {e}")
        return None

def increment_version(version_str):
    parts = version_str.split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)
    return version_str

for addon, info in addons.items():
    print(f"Checking {addon}...")
    latest_tag = get_latest_release(info['repo'])
    if not latest_tag:
        continue

    dockerfile_path = os.path.join(addon, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        continue

    with open(dockerfile_path, "r") as f:
        dockerfile_content = f.read()

    arg_name = info['arg']
    match = re.search(f'ARG {arg_name}="([^"]+)"', dockerfile_content)
    if not match:
        continue

    current_version = match.group(1)

    if latest_tag.startswith('v') and not current_version.startswith('v'):
        clean_tag = latest_tag[1:]
    else:
        clean_tag = latest_tag

    if clean_tag != current_version:
        print(f"Updating {addon} from {current_version} to {clean_tag}")

        # Update Dockerfile
        new_dockerfile_content = re.sub(f'ARG {arg_name}="([^"]+)"', f'ARG {arg_name}="{clean_tag}"', dockerfile_content)
        with open(dockerfile_path, "w") as f:
            f.write(new_dockerfile_content)

        # Update config.yaml
        config_path = os.path.join(addon, "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_content = f.read()

            config_match = re.search(r'version:\s*"([^"]+)"', config_content)
            if config_match:
                current_addon_version = config_match.group(1)
                new_addon_version = increment_version(current_addon_version)
                new_config_content = re.sub(r'version:\s*"([^"]+)"', f'version: "{new_addon_version}"', config_content)
                with open(config_path, "w") as f:
                    f.write(new_config_content)
                print(f"Updated config.yaml version from {current_addon_version} to {new_addon_version}")
    else:
        print(f"{addon} is already up to date ({current_version})")

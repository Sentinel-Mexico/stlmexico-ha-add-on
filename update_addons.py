import urllib.request
import json
import re
import os

ADDONS = {
    "vaultwarden": {
        "repo": "dani-garcia/vaultwarden",
        "var_name": "VAULTWARDEN_VERSION",
        "remove_v": True
    },
    "vikunja": {
        "repo": "go-vikunja/vikunja",
        "var_name": "VIKUNJA_VERSION",
        "remove_v": True
    },
    "linkwarden": {
        "repo": "linkwarden/linkwarden",
        "var_name": "LINKWARDEN_VERSION",
        "remove_v": False
    },
    "affine": {
        "repo": "toeverything/AFFiNE",
        "var_name": "AFFINE_VERSION",
        "remove_v": False
    },
    "syncthing": {
        "repo": "syncthing/syncthing",
        "var_name": "SYNCTHING_VERSION",
        "remove_v": True
    },
    "netdata": {
        "repo": "netdata/netdata",
        "var_name": "NETDATA_VERSION",
        "remove_v": True
    }
}

def get_latest_tag(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest")
    req.add_header("Accept", "application/vnd.github.v3+json")

    # Use token if available
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data["tag_name"]
    except Exception as e:
        print(f"Failed to fetch latest tag for {repo}: {e}")
        return None

def bump_version(version_str):
    parts = version_str.split('.')
    if len(parts) > 0 and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)

def update_addon(addon, config):
    print(f"Checking {addon}...")
    latest_tag = get_latest_tag(config["repo"])
    if not latest_tag:
        return

    dockerfile_path = os.path.join(addon, "Dockerfile")
    config_path = os.path.join(addon, "config.yaml")

    with open(dockerfile_path, "r") as f:
        dockerfile_content = f.read()

    # Handle both quoted and unquoted ARG values
    current_version_match = re.search(f'ARG {config["var_name"]}="?([^"\\s]+)"?', dockerfile_content)
    if not current_version_match:
        print(f"Could not find {config['var_name']} in {dockerfile_path}")
        return

    current_version = current_version_match.group(1)

    target_version = latest_tag
    if config.get("remove_v") and target_version.startswith("v"):
        target_version = target_version[1:]

    if current_version == target_version:
        print(f"{addon} is already up to date ({current_version})")
        return

    print(f"Updating {addon}: {current_version} -> {target_version}")

    new_dockerfile_content = re.sub(
        f'(ARG {config["var_name"]}="?)[^"\\s]+("?)',
        f'\\g<1>{target_version}\\g<2>',
        dockerfile_content
    )

    with open(dockerfile_path, "w") as f:
        f.write(new_dockerfile_content)

    with open(config_path, "r") as f:
        config_content = f.read()

    # Handle both quoted and unquoted version values
    current_config_version_match = re.search(r'^version:\s*"?([^"\\s]+)"?', config_content, flags=re.MULTILINE)
    if current_config_version_match:
        current_config_version = current_config_version_match.group(1)
        new_config_version = bump_version(current_config_version)
        new_config_content = re.sub(
            r'^(version:\s*)"?[^"\\s]+"?(.*)$',
            f'\\g<1>"{new_config_version}"\\g<2>',
            config_content,
            flags=re.MULTILINE
        )
        with open(config_path, "w") as f:
            f.write(new_config_content)
        print(f"Bumped {addon} config.yaml version to {new_config_version}")
    else:
        print(f"Could not find version field in {config_path}")

def main():
    for addon, config in ADDONS.items():
        update_addon(addon, config)

if __name__ == "__main__":
    main()

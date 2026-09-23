import urllib.request
import json
import re
import os
import sys

# Mapping of addon directory to upstream github repo and Dockerfile ARG name
ADDONS = {
    "vaultwarden": {
        "repo": "dani-garcia/vaultwarden",
        "arg_name": "VAULTWARDEN_VERSION",
        "type": "github"
    },
    "vikunja": {
        "repo": "go-vikunja/vikunja",
        "arg_name": "VIKUNJA_VERSION",
        "type": "github"
    },
    "linkwarden": {
        "repo": "linkwarden/linkwarden",
        "arg_name": "LINKWARDEN_VERSION",
        "type": "github"
    },
    "affine": {
        "repo": "toeverything/AFFiNE",
        "arg_name": "AFFINE_VERSION",
        "type": "github"
    },
    "syncthing": {
        "repo": "syncthing/syncthing",
        "arg_name": "SYNCTHING_VERSION",
        "type": "github"
    },
    "netdata": {
        "repo": "netdata/netdata",
        "arg_name": "NETDATA_VERSION",
        "type": "github"
    },
    "freellmapi": {
        "repo": "tashfeenahmed/freellmapi",
        "arg_name": None, # Built from source in Dockerfile, not using tag in FROM directly but let's check
        "type": "github",
        "skip": True # Skipping this one since it's a direct build port and might need manual code updates
    },
    "openspeedtest": {
        "repo": "openspeedtest/Speed-Test",
        "arg_name": None,
        "type": "github",
        "skip": True # uses openspeedtest/latest image directly, no version tag
    }
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("tag_name")
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def update_dockerfile(filepath, arg_name, new_version):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    # Regex to find: ARG SOME_VERSION="old_version"
    pattern = re.compile(rf'(ARG\s+{arg_name}=")([^"]+)(")')

    match = pattern.search(content)
    if not match:
        print(f"Warning: ARG {arg_name} not found in {filepath}")
        return False

    old_version = match.group(2)

    # Optional: if tags from API have 'v' but docker image doesn't, we might need logic.
    # We will strip 'v' if the old version doesn't have it.
    if not old_version.startswith('v') and new_version.startswith('v'):
        clean_new_version = new_version[1:]
    else:
        clean_new_version = new_version

    if old_version == clean_new_version:
        print(f"  Already up-to-date: {old_version}")
        return False

    print(f"  Updating {arg_name} from {old_version} to {clean_new_version}")
    new_content = pattern.sub(rf'\g<1>{clean_new_version}\g<3>', content)

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True

def bump_config_version(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    pattern = re.compile(r'(version:\s*")([^"]+)(")')
    match = pattern.search(content)
    if not match:
        print(f"Warning: version field not found in {filepath}")
        return False

    old_version = match.group(2)

    # Simple semantic version bump for the patch version
    parts = old_version.split('.')
    if len(parts) == 3 and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
        new_version = '.'.join(parts)
        print(f"  Bumping config version from {old_version} to {new_version}")
        new_content = pattern.sub(rf'\g<1>{new_version}\g<3>', content)
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    else:
        print(f"Warning: Could not bump version {old_version} in {filepath}")
        return False

def main():
    changes_made = False

    for addon, details in ADDONS.items():
        if details.get("skip"):
            continue

        print(f"Checking {addon}...")
        repo = details["repo"]
        latest_tag = get_latest_release(repo)

        if not latest_tag:
            print(f"  Failed to get latest tag for {repo}")
            continue

        dockerfile_path = os.path.join(addon, "Dockerfile")
        config_path = os.path.join(addon, "config.yaml")

        updated = update_dockerfile(dockerfile_path, details["arg_name"], latest_tag)
        if updated:
            bump_config_version(config_path)
            changes_made = True

    if changes_made:
        print("Updates applied successfully.")
    else:
        print("All addons are up-to-date.")

if __name__ == "__main__":
    main()
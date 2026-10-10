import os
import json
import urllib.request
import re
import sys

# Configurations
ADDONS = {
    "vaultwarden": {"repo": "dani-garcia/vaultwarden", "strip_v": True},
    "vikunja": {"repo": "go-vikunja/vikunja", "strip_v": True},
    "linkwarden": {"repo": "linkwarden/linkwarden", "strip_v": False},
    "syncthing": {"repo": "syncthing/syncthing", "strip_v": True},
    "netdata": {"repo": "netdata/netdata", "strip_v": True}
}

def get_latest_release(repo_info):
    """Fetches the latest release tag from GitHub API."""
    repo = repo_info["repo"]
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url)

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            tag = data.get("tag_name")
            if not tag:
                return None
            if repo_info["strip_v"] and tag.startswith("v"):
                return tag[1:]
            return tag
    except Exception as e:
        print(f"Error fetching latest release for {repo}: {e}")
        return None

def bump_patch_version(version_str):
    """Increments the patch version of a semver string (e.g., 1.0.1 -> 1.0.2)."""
    parts = version_str.split('.')
    if len(parts) == 3:
        try:
            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
        except ValueError:
            pass
    return version_str

def update_dockerfile(addon, new_version):
    """Updates the ARG <ADDON>_VERSION in the Dockerfile."""
    filepath = os.path.join(addon, "Dockerfile")
    if not os.path.exists(filepath):
        print(f"Dockerfile not found for {addon}")
        return False

    with open(filepath, "r") as f:
        content = f.read()

    # Look for ARG ADDON_VERSION="1.2.3"
    arg_name = f"{addon.upper()}_VERSION"
    pattern = rf'ARG {arg_name}=".*"'
    replacement = f'ARG {arg_name}="{new_version}"'

    new_content = re.sub(pattern, replacement, content)

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        return True
    return False

def update_config_yaml(addon):
    """Bumps the version in config.yaml."""
    filepath = os.path.join(addon, "config.yaml")
    if not os.path.exists(filepath):
        print(f"config.yaml not found for {addon}")
        return False

    with open(filepath, "r") as f:
        lines = f.readlines()

    changed = False
    for i, line in enumerate(lines):
        if line.startswith("version:"):
            # extract current version
            match = re.match(r'version:\s*"([^"]+)"', line)
            if match:
                current_version = match.group(1)
                new_version = bump_patch_version(current_version)
                lines[i] = f'version: "{new_version}"\n'
                changed = True
            break

    if changed:
        with open(filepath, "w") as f:
            f.writelines(lines)
        return True
    return False

def get_current_dockerfile_version(addon):
    """Gets the current ARG <ADDON>_VERSION from Dockerfile."""
    filepath = os.path.join(addon, "Dockerfile")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r") as f:
        content = f.read()

    arg_name = f"{addon.upper()}_VERSION"
    pattern = rf'ARG {arg_name}="(.*)"'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None

def main():
    print("Starting addon updates check...")
    updates_made = []

    for addon, repo_info in ADDONS.items():
        print(f"Checking {addon}...")

        current_version = get_current_dockerfile_version(addon)
        if not current_version:
            print(f"  Failed to read current version for {addon}")
            continue

        latest_version = get_latest_release(repo_info)
        if not latest_version:
            print(f"  Failed to get latest version for {addon}")
            continue

        print(f"  Current: {current_version} | Latest: {latest_version}")

        if current_version != latest_version:
            print(f"  Updating {addon} from {current_version} to {latest_version}...")
            dockerfile_updated = update_dockerfile(addon, latest_version)
            if dockerfile_updated:
                config_updated = update_config_yaml(addon)
                if config_updated:
                    print(f"  Successfully updated {addon}.")
                    updates_made.append(addon)
                else:
                    print(f"  Failed to update config.yaml for {addon}.")
            else:
                print(f"  Failed to update Dockerfile for {addon}.")
        else:
            print(f"  {addon} is up to date.")

    if updates_made:
        print(f"\nUpdates completed for: {', '.join(updates_made)}")
    else:
        print("\nNo updates were necessary.")

if __name__ == "__main__":
    main()

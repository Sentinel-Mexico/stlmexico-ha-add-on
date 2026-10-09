import os
import re
import urllib.request
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

ADDONS = {
    'vaultwarden': 'dani-garcia/vaultwarden',
    'vikunja': 'go-vikunja/vikunja',
    'linkwarden': 'linkwarden/linkwarden',
    'syncthing': 'syncthing/syncthing',
    'netdata': 'netdata/netdata',
}

EXCLUDED_ADDONS = ['freellmapi', 'openspeedtest', 'affine']

def get_latest_github_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url)
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        req.add_header("Authorization", f"Bearer {github_token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get('tag_name')
    except Exception as e:
        logging.error(f"Failed to fetch latest release for {repo}: {e}")
        return None

def update_addon(addon, repo):
    latest_tag = get_latest_github_release(repo)
    if not latest_tag:
        return

    # Strip 'v' prefix if it exists to compare version numbers correctly
    # some repos might use vX.Y.Z, but the Dockerfile expects X.Y.Z (e.g. netdata, syncthing)
    # However, linkwarden uses 'vX.Y.Z' in Dockerfile, vikunja uses 'X.Y.Z', let's check current format

    dockerfile_path = os.path.join(addon, 'Dockerfile')
    if not os.path.exists(dockerfile_path):
        logging.error(f"Dockerfile not found for {addon}")
        return

    with open(dockerfile_path, 'r') as f:
        dockerfile_content = f.read()

    # Find current version
    version_pattern = re.compile(rf'ARG {addon.upper()}_VERSION="([^"]+)"')
    match = version_pattern.search(dockerfile_content)

    if not match:
        logging.error(f"Version ARG not found in {addon}/Dockerfile")
        return

    current_version = match.group(1)

    # Determine the target version string based on current format
    target_version = latest_tag
    if current_version.startswith('v') and not target_version.startswith('v'):
        target_version = f"v{target_version}"
    elif not current_version.startswith('v') and target_version.startswith('v'):
        target_version = target_version[1:]

    if current_version != target_version:
        logging.info(f"[{addon}] Updating from {current_version} to {target_version}")

        # Update Dockerfile
        new_dockerfile_content = dockerfile_content.replace(
            f'ARG {addon.upper()}_VERSION="{current_version}"',
            f'ARG {addon.upper()}_VERSION="{target_version}"'
        )

        with open(dockerfile_path, 'w') as f:
            f.write(new_dockerfile_content)

        # Update config.yaml version
        config_path = os.path.join(addon, 'config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_content = f.read()

            config_version_match = re.search(r'version: "([^"]+)"', config_content)
            if config_version_match:
                ha_version = config_version_match.group(1)
                parts = ha_version.split('.')
                if len(parts) == 3:
                    try:
                        patch = int(parts[2])
                        new_ha_version = f"{parts[0]}.{parts[1]}.{patch + 1}"
                        new_config_content = config_content.replace(
                            f'version: "{ha_version}"',
                            f'version: "{new_ha_version}"'
                        )
                        with open(config_path, 'w') as f:
                            f.write(new_config_content)
                        logging.info(f"[{addon}] Incremented HA add-on version to {new_ha_version}")
                    except ValueError:
                        logging.warning(f"[{addon}] Could not increment version '{ha_version}'")

    else:
        logging.info(f"[{addon}] Already up to date ({current_version})")

def main():
    for addon, repo in ADDONS.items():
        if addon not in EXCLUDED_ADDONS:
            update_addon(addon, repo)

if __name__ == "__main__":
    main()

import os
import json
import re
import urllib.request
import urllib.error

# Mapping of addon directory to upstream repository
ADDONS = {
    "linkwarden": {"repo": "linkwarden/linkwarden", "arg": "LINKWARDEN_VERSION"},
    "netdata": {"repo": "netdata/netdata", "arg": "NETDATA_VERSION"},
    "syncthing": {"repo": "syncthing/syncthing", "arg": "SYNCTHING_VERSION"},
    "vaultwarden": {"repo": "dani-garcia/vaultwarden", "arg": "VAULTWARDEN_VERSION"},
    "vikunja": {"repo": "go-vikunja/vikunja", "arg": "VIKUNJA_VERSION"}
}

def get_latest_release(repo):
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {'User-Agent': 'Mozilla/5.0'}

    # Use GITHUB_TOKEN if available to avoid rate limiting
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("tag_name", "")
    except urllib.error.HTTPError as e:
        print(f"Failed to fetch release for {repo}: {e}")
        return None
    except Exception as e:
        print(f"Error for {repo}: {e}")
        return None

def bump_patch_version(version_str):
    # Bump the last number in "x.y.z"
    parts = version_str.split('.')
    if parts:
        try:
            parts[-1] = str(int(parts[-1]) + 1)
            return '.'.join(parts)
        except ValueError:
            return version_str
    return version_str

def main():
    for addon, config in ADDONS.items():
        print(f"Checking {addon}...")
        latest_tag = get_latest_release(config['repo'])
        if not latest_tag:
            continue

        dockerfile_path = os.path.join(addon, "Dockerfile")
        config_path = os.path.join(addon, "config.yaml")

        if not os.path.exists(dockerfile_path) or not os.path.exists(config_path):
            print(f"  Missing files for {addon}, skipping.")
            continue

        with open(dockerfile_path, 'r') as f:
            dockerfile_content = f.read()

        # Find current version
        arg_name = config['arg']
        match = re.search(rf'ARG {arg_name}="([^"]+)"', dockerfile_content)
        if not match:
            print(f"  Could not find {arg_name} in Dockerfile.")
            continue

        current_version = match.group(1)

        # Clean the latest tag (strip 'v' if current version doesn't have it)
        clean_tag = latest_tag
        if current_version.startswith('v') and not clean_tag.startswith('v'):
            clean_tag = 'v' + clean_tag
        elif not current_version.startswith('v') and clean_tag.startswith('v'):
            clean_tag = clean_tag[1:]

        if current_version == clean_tag:
            print(f"  Up to date: {current_version}")
            continue

        print(f"  Updating {addon}: {current_version} -> {clean_tag}")

        # Update Dockerfile
        new_dockerfile_content = re.sub(
            rf'ARG {arg_name}="[^"]+"',
            f'ARG {arg_name}="{clean_tag}"',
            dockerfile_content
        )

        with open(dockerfile_path, 'w') as f:
            f.write(new_dockerfile_content)

        # Update config.yaml
        with open(config_path, 'r') as f:
            config_content = f.read()

        version_match = re.search(r'^version: "([^"]+)"', config_content, re.MULTILINE)
        if version_match:
            current_addon_version = version_match.group(1)
            new_addon_version = bump_patch_version(current_addon_version)

            new_config_content = re.sub(
                r'^version: "[^"]+"',
                f'version: "{new_addon_version}"',
                config_content,
                count=1,
                flags=re.MULTILINE
            )

            with open(config_path, 'w') as f:
                f.write(new_config_content)

            print(f"  Bumped add-on version: {current_addon_version} -> {new_addon_version}")
        else:
            print(f"  Could not find version in {config_path}")

if __name__ == "__main__":
    main()

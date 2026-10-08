import os
import re
import urllib.request
import json

EXCLUDED_ADDONS = {"freellmapi", "openspeedtest", "affine"}

def get_latest_release(repo_url, token):
    # Extract owner/repo from url
    match = re.search(r'github\.com/([^/]+/[^/]+)', repo_url)
    if not match:
        return None
    repo = match.group(1)

    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api_url, headers={"User-Agent": "update-script"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data["tag_name"]
    except Exception as e:
        print(f"Error fetching {api_url}: {e}")
        return None

def update_addon(addon_dir, token):
    if addon_dir in EXCLUDED_ADDONS or not os.path.isdir(addon_dir):
        return

    config_path = os.path.join(addon_dir, "config.yaml")
    dockerfile_path = os.path.join(addon_dir, "Dockerfile")

    if not os.path.exists(config_path) or not os.path.exists(dockerfile_path):
        return

    # Read config.yaml to get repo url
    with open(config_path, "r") as f:
        config_content = f.read()

    url_match = re.search(r'^url:\s*"?(https://github\.com/[^"\s]+)"?', config_content, re.MULTILINE)
    if not url_match:
        return

    repo_url = url_match.group(1)
    latest_tag = get_latest_release(repo_url, token)
    if not latest_tag:
        return

    # Read Dockerfile to find ARG *_VERSION
    with open(dockerfile_path, "r") as f:
        dockerfile_content = f.read()

    # E.g. ARG NETDATA_VERSION="2.11.0"
    version_match = re.search(r'^ARG\s+([A-Z_]+_VERSION)="(.*)"', dockerfile_content, re.MULTILINE)
    if not version_match:
        return

    arg_name = version_match.group(1)
    current_version = version_match.group(2)

    # Normalize versions for comparison (some repos use 'v' prefix in tags but not in docker images)
    latest_version = latest_tag
    if current_version.startswith("v") and not latest_version.startswith("v"):
        latest_version = "v" + latest_version
    elif not current_version.startswith("v") and latest_version.startswith("v"):
        latest_version = latest_version[1:]

    if current_version == latest_version:
        print(f"{addon_dir}: already up to date ({current_version})")
        return

    print(f"{addon_dir}: updating {current_version} -> {latest_version}")

    # Update Dockerfile
    new_dockerfile_content = re.sub(
        rf'^ARG\s+{arg_name}=".*"',
        f'ARG {arg_name}="{latest_version}"',
        dockerfile_content,
        flags=re.MULTILINE
    )
    with open(dockerfile_path, "w") as f:
        f.write(new_dockerfile_content)

    # Bump version in config.yaml
    def bump_version(match):
        version_str = match.group(1)
        parts = version_str.split(".")
        if len(parts) >= 3:
            parts[-1] = str(int(parts[-1]) + 1)
        return f'version: "{".".join(parts)}"'

    new_config_content = re.sub(
        r'^version:\s*"([^"]+)"',
        bump_version,
        config_content,
        count=1,
        flags=re.MULTILINE
    )
    with open(config_path, "w") as f:
        f.write(new_config_content)

def main():
    token = os.environ.get("GITHUB_TOKEN")
    for item in os.listdir("."):
        if os.path.isdir(item) and not item.startswith("."):
            update_addon(item, token)

if __name__ == "__main__":
    main()

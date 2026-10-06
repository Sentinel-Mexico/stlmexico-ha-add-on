#!/usr/bin/env python3
import urllib.request
import json
import re
import os
import sys

def get_latest_release(repo, use_tags=False):
    token = os.environ.get("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    if use_tags:
        url = f"https://api.github.com/repos/{repo}/tags"

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    if token:
        req.add_header('Authorization', f'token {token}')

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if use_tags:
                return data[0]['name']
            return data['tag_name']
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
        return None

def increment_version(version_str):
    parts = version_str.split('.')
    if len(parts) == 3:
        parts[2] = str(int(parts[2]) + 1)
    else:
        parts.append('1')
    return '.'.join(parts)

# Map of addon -> (github_repo, dockerfile_arg_name, keep_v_prefix, use_tags_api)
repos = {
    "linkwarden": ("linkwarden/linkwarden", "LINKWARDEN_VERSION", True, False),
    "netdata": ("netdata/netdata", "NETDATA_VERSION", False, False),
    "syncthing": ("syncthing/syncthing", "SYNCTHING_VERSION", False, False),
    "vaultwarden": ("dani-garcia/vaultwarden", "VAULTWARDEN_VERSION", False, False),
    "vikunja": ("go-vikunja/vikunja", "VIKUNJA_VERSION", False, False)
}

def main():
    for addon, (repo, version_arg, keep_v, use_tags) in repos.items():
        latest_tag = get_latest_release(repo, use_tags)
        if not latest_tag:
            continue

        clean_tag = latest_tag
        if not keep_v and latest_tag.startswith('v'):
            clean_tag = latest_tag[1:]

        print(f"Checking {addon}... Latest release: {clean_tag} (raw tag: {latest_tag})")

        dockerfile_path = f"{addon}/Dockerfile"
        config_path = f"{addon}/config.yaml"

        try:
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()

            current_version_match = re.search(f'ARG {version_arg}="([^"]+)"', dockerfile_content)
            if not current_version_match:
                print(f"Could not find ARG {version_arg} in {dockerfile_path}")
                continue

            current_version = current_version_match.group(1)

            if current_version != clean_tag:
                print(f"  Update needed! {current_version} -> {clean_tag}")

                # Update Dockerfile
                new_dockerfile = dockerfile_content.replace(f'ARG {version_arg}="{current_version}"', f'ARG {version_arg}="{clean_tag}"')
                with open(dockerfile_path, 'w') as f:
                    f.write(new_dockerfile)

                # Update config.yaml
                with open(config_path, 'r') as f:
                    config_content = f.read()

                current_config_version_match = re.search(r'version: "([^"]+)"', config_content)
                if current_config_version_match:
                    current_config_version = current_config_version_match.group(1)
                    new_config_version = increment_version(current_config_version)

                    new_config = config_content.replace(f'version: "{current_config_version}"', f'version: "{new_config_version}"', 1)
                    with open(config_path, 'w') as f:
                        f.write(new_config)
                    print(f"  Updated config.yaml version {current_config_version} -> {new_config_version}")
                else:
                    print(f"  Could not find version in {config_path}")
            else:
                print(f"  Already up to date ({current_version}).")

        except Exception as e:
            print(f"Error processing {addon}: {e}")

if __name__ == "__main__":
    main()

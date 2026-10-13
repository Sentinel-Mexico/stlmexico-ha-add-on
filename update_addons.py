import urllib.request
import json
import re
import os

repos = {
    "linkwarden": {"repo": "linkwarden/linkwarden", "docker_arg": "LINKWARDEN_VERSION"},
    "vaultwarden": {"repo": "dani-garcia/vaultwarden", "docker_arg": "VAULTWARDEN_VERSION"},
    "netdata": {"repo": "netdata/netdata", "docker_arg": "NETDATA_VERSION"},
    "syncthing": {"repo": "syncthing/syncthing", "docker_arg": "SYNCTHING_VERSION"},
    "vikunja": {"repo": "go-vikunja/vikunja", "docker_arg": "VIKUNJA_VERSION"}
}

def bump_version(version):
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    return '.'.join(parts)

for addon, data in repos.items():
    print(f"Checking {addon}...")
    url = f"https://api.github.com/repos/{data['repo']}/releases/latest"
    req = urllib.request.Request(url)

    # Try getting GITHUB_TOKEN to avoid rate limits
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as response:
            release_data = json.loads(response.read().decode())
            latest_version = release_data['tag_name']

            # Format version correctly based on existing Dockerfile
            dockerfile_path = f"{addon}/Dockerfile"
            if not os.path.exists(dockerfile_path):
                continue

            with open(dockerfile_path, 'r') as f:
                content = f.read()

            match = re.search(f'ARG {data["docker_arg"]}="([^"]+)"', content)
            if not match:
                continue

            current_version = match.group(1)

            # Some projects strip the 'v', some don't. Try to match the format of current_version
            if not current_version.startswith('v') and latest_version.startswith('v'):
                formatted_latest_version = latest_version[1:]
            else:
                formatted_latest_version = latest_version

            if current_version != formatted_latest_version:
                print(f"Updating {addon}: {current_version} -> {formatted_latest_version}")

                # Update Dockerfile
                new_content = re.sub(f'ARG {data["docker_arg"]}="[^"]+"', f'ARG {data["docker_arg"]}="{formatted_latest_version}"', content)
                with open(dockerfile_path, 'w') as f:
                    f.write(new_content)

                # Update config.yaml version
                config_path = f"{addon}/config.yaml"
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_content = f.read()

                    version_match = re.search(r'^version:\s+"([^"]+)"', config_content, re.MULTILINE)
                    if version_match:
                        current_config_version = version_match.group(1)
                        new_config_version = bump_version(current_config_version)
                        print(f"Bumping {addon}/config.yaml version: {current_config_version} -> {new_config_version}")

                        new_config_content = re.sub(r'^version:\s+"([^"]+)"', f'version: "{new_config_version}"', config_content, flags=re.MULTILINE)
                        with open(config_path, 'w') as f:
                            f.write(new_config_content)
            else:
                print(f"{addon} is already up to date ({current_version})")

    except Exception as e:
        print(f"Error checking {addon}: {e}")

import os
import subprocess
import click
from gish.config import load_profiles, save_profiles

def generate_ssh_key(name, email):
    ssh_dir = os.path.expanduser("~/.ssh")
    key_path = os.path.join(ssh_dir, f"{name}")
    
    # Generate the SSH key
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", email, "-f", key_path, "-N", ""], check=True)
    
    # Add the SSH key to the SSH agent
    subprocess.run(["ssh-add", key_path], check=True)
    
    # Return the path to the public key
    return f"{key_path}.pub"

def add_ssh_key_to_github(name, key_path):
    with open(key_path, "r") as key_file:
        public_key = key_file.read()
    
    # This is a simple example; in a real case, you would make a call to the GitHub API
    click.echo(f"Add the following SSH key to your GitHub account:\n{public_key}")

def add_profile_ssh(name, email):
    profiles = load_profiles()

    if name in profiles:
        raise ValueError(f"Profile '{name}' already exists.")

    # Generate the SSH key
    key_path = generate_ssh_key(name, email)
    
    # Save the profile
    profiles[name] = {"ssh_key_path": key_path}
    save_profiles(profiles)
    
    # Instruction to add the key to GitHub
    add_ssh_key_to_github(name, key_path)

def switch_profile_ssh(name):
    profiles = load_profiles()
    
    if name not in profiles:
        raise ValueError(f"Profile '{name}' not found.")

    ssh_key_path = profiles[name]["ssh_key_path"].replace(".pub", "")

    # Remove all SSH keys from the agent
    try:
        subprocess.run(["ssh-add", "-D"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error removing existing SSH keys from the agent: {e}")

    # Add the new SSH key to the agent
    try:
        subprocess.run(["ssh-add", ssh_key_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error adding SSH key for profile '{name}' to the agent: {e}")

    return name

def check_status():
    """Checks the status of the GitHub profile configuration and returns the active profile."""
    profiles = load_profiles()
    
    if not profiles:
        return "No profiles configured."
    
    try:
        result = subprocess.run(["ssh-add", "-l"], capture_output=True, text=True, check=True)
        loaded_keys = result.stdout
    except FileNotFoundError:
        return "The 'ssh-add' command was not found. Check if the SSH agent is running."
    except subprocess.CalledProcessError as e:
        return f"Error listing SSH keys loaded in the agent: {e}\nError output: {e.stderr}"

    active_profile = None
    for name, data in profiles.items():
        ssh_key_path = data["ssh_key_path"].replace(".pub", "")

        try:
            key_fingerprint = subprocess.run(
                ["ssh-keygen", "-lf", ssh_key_path + ".pub"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"Error getting the fingerprint of the key for profile '{name}': {e}\nError output: {e.stderr}"
        
        if key_fingerprint in loaded_keys:
            try:
                # Test the SSH connection with GitHub
                result = subprocess.run(
                    "ssh -T git@github.com", shell=True, capture_output=True, text=True
                )

                if "Hi" in result.stderr:
                    active_profile = name
                    break
                else:
                    return "The SSH key is not properly configured for authentication with GitHub."
            except subprocess.CalledProcessError as e:
                return f"Error testing SSH connection with GitHub: {e}\nError output: {e.stderr}"
    
    if active_profile:
        return f"Active Profile: {active_profile}"
    else:
        return "No active profile found."

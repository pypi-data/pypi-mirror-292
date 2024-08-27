# git_utils.py

import subprocess

def is_git_repo():
    try:
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True, check=True)
        return result.stdout.strip() == 'true'
    except subprocess.CalledProcessError:
        return False

def get_commit_hash():
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_git_diff():
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_remote_url():
    try:
        result = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_repo_name(remote_url):
    if remote_url:
        return remote_url.split('/')[-1].replace('.git', '')
    return None

def get_current_branch():
    try:
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_last_commit_message():
    try:
        result = subprocess.run(["git", "log", "-1", "--pretty=%B"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_last_commit_author():
    try:
        result = subprocess.run(["git", "log", "-1", "--pretty=format:%an <%ae>"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_last_commit_date():
    try:
        result = subprocess.run(["git", "log", "-1", "--pretty=format:%ad"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

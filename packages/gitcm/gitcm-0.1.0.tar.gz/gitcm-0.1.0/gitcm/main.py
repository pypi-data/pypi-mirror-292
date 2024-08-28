import subprocess

def generate_commit_message():
    return "Test Message"

def git_commit():
    commit_message = generate_commit_message()

    try:
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"Committed with message: {commit_message}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    git_commit()
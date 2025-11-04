import os

# Take user inputs
dti = input("Enter the Issue Key (e.g IDT-10): ")
commit_msg = input("Enter the Commit message: ")
full_commit_msg = f"{dti} - {commit_msg}"

# Perform git operations
os.system("git checkout -- core/settings.py")
os.system("git add .")
os.system(f'git commit -m "{full_commit_msg}"')
os.system("git push origin")
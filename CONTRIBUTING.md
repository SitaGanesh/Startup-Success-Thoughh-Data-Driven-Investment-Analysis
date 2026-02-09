# 🤝 Contribution Guide

Working with project- a guide, contributing to the **Startup Success Through Data-Driven Investment Analysis** project!  
This guide explains how to set up the project locally, create your own branch, make changes, and safely contribute back to the main branch.

---

## 🧑‍💻 Prerequisites

Make sure you have these installed:
- Git  
- Python (>= 3.9 recommended)  
- Virtualenv (optional but recommended)  
- VS Code or any code editor  

---

## 🚀 Step 1: Clone the Repository

1. Open a new folder on your laptop.
2. Open Terminal in that folder.
3. Run:

```bash
git clone https://github.com/SitaGanesh/Startup-Success-Thoughh-Data-Driven-Investment-Analysis.git
```

Move into the project folder (you can use tab for autocomplete):

```bash
cd Startup-Success-Thoughh-Data-Driven-Investment-Analysis
```

## Step 2: Create Your Own Branch

Better create branch name your name, create a branch like:

```bash
git checkout -b ganesh
```

You can also use formats like:
```bash
git checkout -b ganesh-feature-x
git checkout -b ganesh-ui-update
```

Check that you're on your new branch:

```bash
git branch
```

## 🛠️ Step 3: Set Up Environment (Recommended)
Create virtual environment:
```bash
python -m venv venv
```

Activate it:

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Step 4: Make Your Changes
You can:

- Improve ML models
- Add features
- Improve UI
- Fix bugs
- Improve documentation

Run tests / scripts before committing to ensure nothing breaks.


## Step 5: Commit Your Changes
Check changed files:
```bash
git status
```
Add files:
```bash
git add .
```
Commit with a meaningful message:
```bash
git commit -m "Added feature engineering improvements"
```

## Step 6: Merge Your Branch into Main (Local)
Before merging, make sure you have the latest changes from the main branch:
```bash
git checkout main
```
Pull latest changes:
```bash
git pull origin main
```
If in case: 


Any conflicts, switch back to your branch and merge main into it first:
```bash
git checkout ganesh
git merge main
```

Resolve any conflicts if they appear, then:

```bash
git checkout main
git merge ganesh
```

## Step 7: Push Changes to GitHub
Push your changes to the remote repository:
```bash
git push origin main
```

Alternative Workflow (Recommended for Collaboration):
Instead of merging directly to main, push your branch and create a Pull Request:
```bash
git push origin ganesh
```
Then go to GitHub and create a Pull Request for review.

## 🔀 Step 8: Pull Request (Recommended Workflow)
Best practice:

1. Push your branch:
```bash
git push origin ganesh
```
2. Open GitHub repo

3. Click Compare & Pull Request

4. Describe what you changed

5. Wait for review and approval


## Additional Resources
Useful Git Commands
```bash
# Check status of your files
git status

# View commit history
git log

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard

# View differences
git diff

# Update your local repository
git fetch origin

# Delete a branch
git branch -d branch-name

```

### Thankyou.

# GitHub Force Push Commands for LEXICON

## Complete Repository Replacement

These commands will completely replace the contents of https://github.com/dr-jd-allen/lexicon with your new LEXICON MVP Alpha.

### Step 1: Configure Git
```bash
cd C:\Users\jdall\lexicon-mvp-alpha

# Set your Git credentials
git config user.email "jdall@example.com"  # Replace with your email
git config user.name "Dr. JD Allen"        # Replace with your name
```

### Step 2: Add Remote Repository
```bash
# Add your existing GitHub repo as the remote
git remote add origin https://github.com/dr-jd-allen/lexicon.git

# Verify the remote was added
git remote -v
```

### Step 3: Stage All Files
```bash
# Add all files (respecting .gitignore)
git add .

# Verify what will be committed (check no .env files are included)
git status

# Check LFS files are tracked
git lfs ls-files
```

### Step 4: Create Initial Commit
```bash
# Create the initial commit
git commit -m "Initial commit: LEXICON MVP Alpha v0.1.5

- Multi-agent AI legal research system
- Specialized for TBI Daubert motions
- Includes document corpus (anonymized)
- Docker-based deployment
- React frontend with WebSocket support"
```

### Step 5: Force Push to Replace Repository
```bash
# This will COMPLETELY REPLACE everything in the remote repository
git push --force origin main

# If the remote uses 'master' instead of 'main':
# git push --force origin main:master
```

### Alternative: If Remote Has Different Branch Name
```bash
# Check what branches exist on remote
git ls-remote --heads origin

# If it shows 'master' instead of 'main', use:
git push --force origin main:master

# Or rename your local branch to match:
git branch -M master
git push --force origin master
```

## What This Does

- ✅ Completely replaces ALL content in the remote repository
- ✅ Removes all previous commit history
- ✅ Uploads all files respecting .gitignore rules
- ✅ Uploads large files via Git LFS
- ⚠️ This is IRREVERSIBLE - the old repository content will be gone

## After Push Checklist

1. **Verify on GitHub**:
   - All files are present
   - No .env files were uploaded
   - Large files show "Stored with Git LFS"
   - Repository is still set to Private

2. **Update Repository Settings**:
   ```
   Go to: https://github.com/dr-jd-allen/lexicon/settings
   
   - General > Default branch: Ensure it's 'main' or 'master'
   - Branches > Add rule > Protect main branch
   - Manage access > Verify team members
   ```

3. **Update Repository Description**:
   - Add description: "LEXICON - AI-powered legal research and brief writing system"
   - Add topics: legal-tech, ai, machine-learning, nlp, tort-law

## Troubleshooting

If push is rejected:
```bash
# Check current branch
git branch

# Check remote branches
git ls-remote --heads origin

# If needed, set upstream and force
git push --set-upstream origin main --force
```

If LFS files fail:
```bash
# Verify LFS is initialized
git lfs install

# Re-track files if needed
git lfs track "*.pdf"
git add .gitattributes
git commit -m "Update LFS tracking"
```

## Team Access

After successful push, team members can clone with:
```bash
git clone https://github.com/dr-jd-allen/lexicon.git
cd lexicon
git lfs pull  # Ensures all LFS files are downloaded
```
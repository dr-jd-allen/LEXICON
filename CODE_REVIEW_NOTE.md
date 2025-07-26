# Code Review Branch

This is a lightweight branch created specifically for code review purposes.

## What's Different

- **Removed**: `tbi-corpus/` directory containing all legal documents (PDFs, DOCs)
- **Removed**: Large image files and JSON data files
- **Kept**: All source code, configuration files, and documentation

## Why This Branch Exists

The main branch includes a large corpus of legal documents (>100MB) tracked with Git LFS, which can cause issues with some code review tools. This branch contains only the code and configuration files needed for review.

## To Review the Full Project

For the complete project including the document corpus, use the `main` branch.
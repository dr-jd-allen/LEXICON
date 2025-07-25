# LEXICON Quick Start Guide

## Welcome to LEXICON!

LEXICON is your AI-powered legal brief generation system, designed specifically for traumatic brain injury (TBI) cases.

## 🚀 Getting Started

### 1. First Launch
When you first open LEXICON, you'll see:
- **System Tray Icon**: Look for the LEXICON icon (⚖️) in your system tray
- **Automatic Browser Launch**: Your default browser will open to http://localhost

### 2. System Tray Menu
Right-click the LEXICON icon in your system tray to access:
- **Open LEXICON**: Opens the web interface
- **Open Documents Folder**: Quick access to your briefs
- **Backup Now**: Create an immediate backup
- **Services**: Restart or stop LEXICON services
- **Settings**: Configure API keys and preferences
- **Help**: Access this guide and support

## 📄 Generating Your First Brief

### Step 1: Upload Documents
1. Click "Open LEXICON" from the system tray
2. Drag and drop your case documents:
   - Expert reports
   - Depositions
   - Medical records
   - Court orders
3. Documents are automatically anonymized for HIPAA compliance

### Step 2: Select Brief Type
Choose your motion type:
- **Daubert Motion**: To exclude expert testimony
- **Response to Daubert**: To defend your expert
- **Motion in Limine**: Other evidentiary challenges

### Step 3: Identify the Expert
- Enter the expert's name
- Select challenge or support strategy

### Step 4: Generate
Click "Generate Brief" and watch as 5 AI agents work together:
1. **Claude Opus 4**: Analyzes your case
2. **o3-pro**: Searches legal precedents
3. **o4-mini**: Reviews medical literature
4. **GPT-4.5**: Writes your brief
5. **Gemini 2.5**: Fact-checks and formats

## 📁 Finding Your Documents

All generated documents are saved to:
```
C:\Users\[YourName]\Documents\LEXICON\
├── Generated Briefs\
├── Uploaded Documents\
└── Strategic Recommendations\
```

Access quickly via:
- System tray → "Open Documents Folder"
- Desktop shortcut: "LEXICON Documents"

## 🔒 Security & Privacy

- **Local Storage**: All data stays on your computer
- **HIPAA Compliant**: Automatic document anonymization
- **Encrypted**: Secure storage of sensitive information
- **Daily Backups**: Automatic at 2 AM

## ⚡ Tips for Best Results

### Document Quality
- Upload clear, searchable PDFs
- Include complete expert reports
- Provide relevant depositions
- Add medical records when applicable

### Optimal Usage
- **Challenge Strategy**: Focus on methodology weaknesses
- **Support Strategy**: Emphasize credentials and acceptance
- **Be Specific**: Provide expert's full name
- **Context Matters**: More documents = better results

## 🛠️ Troubleshooting

### LEXICON Won't Start
1. Check system tray for the icon
2. Ensure Docker Desktop is running
3. Right-click tray icon → Services → Restart Services

### Cannot Access Web Interface
1. Wait 30 seconds after starting
2. Try http://localhost in your browser
3. Check Windows Firewall settings

### Brief Generation Fails
1. Verify API keys in Settings
2. Check internet connection
3. Ensure sufficient disk space

## 📞 Getting Help

### Quick Support
- **In-App Help**: System tray → Help → Support Website
- **Logs**: System tray → Services → View Logs
- **Email**: support@lexicon-ai.com

### Common Questions

**Q: How long does brief generation take?**
A: Typically 3-5 minutes depending on document complexity

**Q: Can I edit the generated brief?**
A: Yes! Briefs are saved as editable Word documents

**Q: Is my data secure?**
A: All processing happens locally. No data leaves your computer.

**Q: How do I update LEXICON?**
A: Updates are automatic. You'll see a notification when available.

## 🎯 Pro Tips

1. **Batch Processing**: Upload multiple related documents at once
2. **Strategic Recommendations**: Always review the separate recommendations document
3. **Citation Check**: All citations are verified by Gemini's fact-checker
4. **Version Control**: Each brief includes timestamp in filename

## 📊 Understanding the Output

Each LEXICON session produces:
1. **Legal Brief** (15-30 pages)
   - Fully formatted with proper citations
   - Ready for filing
   - MLA 9th edition style

2. **Strategic Recommendations** (3-5 pages)
   - Pre-trial strategy
   - Deposition questions
   - Settlement considerations
   - Alternative approaches

3. **Generation Metrics**
   - Word count
   - Citations verified
   - Processing time
   - Agents used

---

**Remember**: LEXICON is a tool to enhance your legal practice. Always review and customize the output to match your specific case needs and local rules.

© 2024 Allen Law Group | LEXICON v1.0
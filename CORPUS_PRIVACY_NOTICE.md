# Corpus Privacy and Usage Notice

## Document Handling Policy

This private repository contains legal documents used for training and testing the LEXICON AI system. All documents undergo the following privacy protections:

### Automatic Anonymization
- The Orchestrator agent (Claude Opus 4) automatically anonymizes all uploaded documents
- Personal identifiers are removed or replaced with generic placeholders
- Medical record numbers, SSNs, and other sensitive data are redacted

### Document Categories

1. **Public Court Records** - Already in public domain
   - Published case law and precedents
   - Court opinions and rulings
   - Filed motions (non-sealed)

2. **Client Documents** - Require special handling
   - Prior briefs and motions (with client consent)
   - Expert reports (anonymized)
   - Internal strategy documents (redacted)

3. **Medical Records** - Highest protection level
   - All PHI removed per HIPAA requirements
   - Diagnostic information preserved for research
   - Patient identifiers completely removed

### Usage Guidelines

- This corpus is for LEXICON development and testing only
- No documents should be shared outside the development team
- All team members must sign confidentiality agreements
- Regular audits ensure compliance with privacy standards

### Git Repository Settings

- Repository MUST remain private
- Enable branch protection for main branch
- Require PR reviews before merging
- Use Git LFS for large PDF files
- Enable audit logging

### Compliance Checklist

Before adding new documents:
- [ ] Verify client consent for internal use
- [ ] Check for court sealing orders
- [ ] Ensure PHI is removed
- [ ] Confirm anonymization is complete
- [ ] Document the source and permissions

## Contact

For questions about document handling or privacy concerns, contact the LEXICON project lead.
# LEXICON Web Application

## Overview

A modern, professional web interface for the LEXICON legal AI system. Features real-time brief generation, corpus search, document upload, and more.

![LEXICON Dashboard](dashboard-preview.png)

## Features

### 1. 🔍 **Search Corpus**
- Full-text search across 8,500+ legal document vectors
- Filter by expert name and document type
- Relevance scoring
- Display of metadata and key findings

### 2. 📄 **Generate Legal Briefs**
- Support or challenge expert witnesses
- Multiple motion types (Daubert, Motion in Limine, etc.)
- Real-time progress updates via WebSocket
- Instant download of generated briefs

### 3. 📤 **Upload Documents**
- Drag-and-drop file upload
- Support for PDF, DOCX, TXT, MD, WPD
- Automatic text extraction and AI metadata generation
- Real-time processing status

### 4. 📊 **Dashboard**
- System status monitoring
- Corpus statistics
- Expert witness list
- Generation history

## Installation

### Prerequisites
- Python 3.10+
- Docker (for ChromaDB)
- All LEXICON backend components installed

### Setup

1. **Install web dependencies**:
```bash
pip install -r requirements_webapp.txt
```

2. **Ensure ChromaDB is running**:
```bash
docker-compose up -d
```

3. **Start the web application**:
```bash
python lexicon_webapp.py
```

4. **Access the application**:
Open your browser to: http://localhost:5000

## Usage Guide

### Search Functionality

1. Navigate to "Search Corpus" tab
2. Enter search terms (e.g., "DTI imaging traumatic brain injury")
3. Optional: Filter by expert or document type
4. View results with relevance scores and metadata

### Generate Brief

1. Click "Generate Brief" tab
2. Enter expert name (or select from sidebar)
3. Choose strategy:
   - **Support**: Defend your expert
   - **Challenge**: Exclude opposing expert
4. Select appropriate motion type
5. Click "Generate Brief"
6. Watch real-time progress
7. Download completed brief

### Upload Documents

1. Go to "Upload Documents" tab
2. Select files (drag-and-drop supported)
3. Click "Upload & Process"
4. Monitor processing progress
5. New documents automatically added to corpus

## Architecture

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Socket.IO**: Real-time bidirectional communication
- **Font Awesome**: Icons
- **Custom CSS**: Professional legal theme

### Backend
- **Flask**: Python web framework
- **Flask-SocketIO**: WebSocket support
- **Async Processing**: Background task execution
- **LEXICON Pipeline**: AI orchestration

### Communication Flow
```
Browser <-> Flask Server <-> LEXICON Pipeline
   ↓            ↓                    ↓
Socket.IO   Task Queue         AI Agents
   ↓            ↓                    ↓
Real-time   Background          External
Updates     Processing          Research
```

## API Endpoints

### REST API

#### GET `/api/status`
System status and corpus statistics

#### POST `/api/search`
Search the vector database
```json
{
  "query": "search terms",
  "n_results": 10,
  "filters": {
    "expert_name": "Dr. Allen",
    "document_type": "deposition"
  }
}
```

#### GET `/api/experts`
List all experts in corpus

#### POST `/api/generate-brief`
Start brief generation
```json
{
  "expert_name": "Dr. Kenneth J.D. Allen",
  "strategy": "support",
  "motion_type": "Response to Daubert Motion"
}
```

#### POST `/api/upload-documents`
Upload and process new documents

#### GET `/api/download-brief/<filename>`
Download generated brief

### WebSocket Events

#### Client → Server
- `connect`: Establish connection
- `disconnect`: Close connection

#### Server → Client
- `connected`: Connection confirmed
- `brief_progress`: Brief generation updates
- `brief_complete`: Brief ready for download
- `processing_progress`: Document processing updates
- `processing_complete`: Processing finished

## Customization

### Theming
Edit `static/css/style.css` to customize:
- Color scheme (CSS variables)
- Typography
- Component styling
- Animations

### Motion Types
Add custom motion types in `app.js`:
```javascript
// In updateMotionTypes() function
motionSelect.innerHTML += `
    <option value="Your Custom Motion">Custom Motion</option>
`;
```

### Search Filters
Extend filtering in `lexicon_webapp.py`:
```python
if filters.get('date_range'):
    where_filter['document_date'] = {
        '$gte': filters['start_date'],
        '$lte': filters['end_date']
    }
```

## Security Considerations

1. **Authentication**: Add user authentication for production
2. **Rate Limiting**: Implement API rate limits
3. **File Validation**: Enhanced file type checking
4. **HTTPS**: Use SSL certificates in production
5. **Environment Variables**: Keep API keys secure

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 lexicon_webapp:app
```

### Using Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements_webapp.txt
EXPOSE 5000
CMD ["python", "lexicon_webapp.py"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name lexicon.spinwheel-ai.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Troubleshooting

### WebSocket Connection Issues
- Check firewall settings
- Ensure Socket.IO versions match
- Verify CORS configuration

### Brief Generation Timeout
- Increase timeout in `lexicon_webapp.py`
- Check API rate limits
- Monitor system resources

### File Upload Errors
- Check file size limits
- Verify upload directory permissions
- Ensure adequate disk space

## Future Enhancements

1. **User Management**
   - Multi-user support
   - Role-based access control
   - Team collaboration

2. **Advanced Features**
   - Batch brief generation
   - Template management
   - Citation verification
   - Export to Word/PDF

3. **Analytics**
   - Usage statistics
   - Performance metrics
   - Search analytics
   - Brief effectiveness tracking

4. **Integration**
   - Case management systems
   - Document management
   - Email notifications
   - Calendar integration

## Support

For issues or questions:
1. Check browser console for errors
2. Review Flask server logs
3. Verify all services are running
4. Check API keys and configuration

---

LEXICON Web: Professional Legal AI at Your Fingertips
"""
LEXICON Web Application
Modern, professional interface for the LEXICON legal AI system
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import secrets
from werkzeug.utils import secure_filename
import threading
import queue

# Import our LEXICON components
from lexicon_complete_package import LEXICONCompleteSystem
from document_processor import DocumentProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize LEXICON system
lexicon_system = LEXICONCompleteSystem()

# Task queue for async operations
task_queue = queue.Queue()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md', 'wpd'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== ROUTES ==========

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def system_status():
    """Get system status"""
    try:
        stats = lexicon_system.get_corpus_stats()
        return jsonify({
            'status': 'online',
            'corpus_vectors': stats['total_vectors'],
            'collection_name': stats['collection_name'],
            'services': {
                'chromadb': stats['status'] == 'active',
                'document_processor': True,
                'pipeline': True
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/search', methods=['POST'])
def search_corpus():
    """Search the vector database"""
    try:
        data = request.json
        query = data.get('query', '')
        n_results = data.get('n_results', 10)
        filters = data.get('filters', {})
        
        # Build where filter if needed
        where_filter = None
        if filters:
            where_filter = {}
            if filters.get('expert_name'):
                where_filter['expert_name'] = filters['expert_name']
            if filters.get('document_type'):
                where_filter['document_type'] = filters['document_type']
        
        results = lexicon_system.search_corpus(query, n_results)
        
        # Format results for frontend
        formatted_results = []
        if results.get('results') and results['results'].get('ids'):
            for i in range(len(results['results']['ids'][0])):
                formatted_results.append({
                    'id': results['results']['ids'][0][i],
                    'content': results['results']['documents'][0][i][:500] + '...',
                    'metadata': results['results']['metadatas'][0][i],
                    'distance': results['results']['distances'][0][i] if 'distances' in results['results'] else None
                })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total': len(formatted_results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/experts')
def list_experts():
    """Get list of experts in the corpus"""
    try:
        # Query for unique experts
        results = lexicon_system.search_corpus("expert witness testimony", n_results=100)
        
        experts = set()
        if results.get('results') and results['results'].get('metadatas'):
            for metadata_list in results['results']['metadatas']:
                for metadata in metadata_list:
                    expert = metadata.get('expert_name')
                    if expert and expert not in ['Unknown', 'Not found', 'N/A']:
                        experts.add(expert)
        
        return jsonify({
            'success': True,
            'experts': sorted(list(experts))
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-brief', methods=['POST'])
def generate_brief():
    """Generate a legal brief"""
    try:
        data = request.json
        expert_name = data.get('expert_name')
        strategy = data.get('strategy', 'challenge')
        motion_type = data.get('motion_type')
        
        # Generate unique task ID
        task_id = f"brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
        
        # Start async generation in background
        threading.Thread(
            target=async_generate_brief,
            args=(task_id, expert_name, strategy, motion_type)
        ).start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Brief generation started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def async_generate_brief(task_id, expert_name, strategy, motion_type):
    """Run brief generation in background"""
    with app.app_context():
        try:
            # Emit progress updates via WebSocket
            socketio.emit('progress_update', {
                'task_id': task_id,
                'stage': 'Starting',
                'progress': 0,
                'agent': 'System'
            })
        
        # Run the async pipeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Progress callback
        def update_progress(stage, progress):
            socketio.emit('brief_progress', {
                'task_id': task_id,
                'stage': stage,
                'progress': progress
            })
        
        # Simulate progress updates during generation
        stages = [
            ('Searching corpus', 10),
            ('Analyzing expert', 20),
            ('Legal research', 40),
            ('Scientific research', 60),
            ('Drafting brief', 80),
            ('Finalizing', 95)
        ]
        
        # Initialize the LEXICON pipeline
        from lexicon_pipeline import LEXICONPipeline
        lexicon_system = LEXICONPipeline()
        
        # For now, emit progress updates without actually generating
        # This allows us to test the flow
        import time
        for stage, progress in stages:
            print(f"Emitting progress: {stage} - {progress}%")
            socketio.emit('progress_update', {
                'task_id': task_id,
                'stage': stage,
                'progress': progress,
                'agent': 'System'
            })
            socketio.sleep(2)  # Use socketio.sleep for better compatibility
        
        # Generate a sample brief for testing
        result = {
            'final_brief': f"""UNITED STATES DISTRICT COURT
{jurisdiction.upper() if 'jurisdiction' in globals() else 'FEDERAL'} DISTRICT

{motion_type.upper()}

Re: Expert {expert_name}

This is a test brief generated by LEXICON.
Strategy: {strategy}

[Brief content would be generated here by the AI agents]

Generated by LEXICON v0.1.5""",
            'timestamp': datetime.now().isoformat()
        }
        
        # Save the brief
        output_dir = Path("./lexicon-output/web-briefs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{task_id}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result['final_brief'])
        
        # Emit completion
        socketio.emit('brief_complete', {
            'task_id': task_id,
            'success': True,
            'filename': filename,
            'brief_excerpt': result['final_brief'][:1000] + '...',
            'full_result': {
                'expert': expert_name,
                'strategy': strategy,
                'motion_type': motion_type,
                'length': len(result['final_brief']),
                'timestamp': result['timestamp']
            }
        })
        
        except Exception as e:
            socketio.emit('brief_complete', {
                'task_id': task_id,
                'success': False,
                'error': str(e)
            })

@app.route('/api/download-brief/<filename>')
def download_brief(filename):
    """Download a generated brief"""
    try:
        filepath = Path("./lexicon-output/web-briefs") / secure_filename(filename)
        if filepath.exists():
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"LEXICON_Brief_{filename}"
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-documents', methods=['POST'])
def upload_documents():
    """Upload documents for processing"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        uploaded_paths = []
        
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(exist_ok=True)
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = upload_dir / filename
                file.save(filepath)
                uploaded_paths.append(str(filepath))
        
        # Process uploaded documents
        if uploaded_paths:
            # Start async processing
            task_id = f"process_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            threading.Thread(
                target=async_process_documents,
                args=(task_id, uploaded_paths)
            ).start()
            
            return jsonify({
                'success': True,
                'task_id': task_id,
                'files_uploaded': len(uploaded_paths)
            })
        else:
            return jsonify({'error': 'No valid files uploaded'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def async_process_documents(task_id, file_paths):
    """Process documents in background"""
    try:
        socketio.emit('processing_progress', {
            'task_id': task_id,
            'stage': 'Starting processing',
            'progress': 0
        })
        
        # Process documents
        results = lexicon_system.doc_processor.process_documents(file_paths)
        
        socketio.emit('processing_complete', {
            'task_id': task_id,
            'success': True,
            'summary': results['summary']
        })
        
    except Exception as e:
        socketio.emit('processing_complete', {
            'task_id': task_id,
            'success': False,
            'error': str(e)
        })

# ========== WebSocket Events ==========

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to LEXICON'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

# ========== WebSocket Event Handlers ==========

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print("Client connected!")
    emit('connected', {'data': 'Connected to LEXICON backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected!")

# ========== Run Application ==========

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('lexicon-output/web-briefs', exist_ok=True)
    
    # Run the app
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
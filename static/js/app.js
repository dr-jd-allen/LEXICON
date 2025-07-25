// LEXICON Web Application JavaScript

// Initialize Socket.IO
const socket = io();

// Global variables
let currentBriefTask = null;
let currentProcessTask = null;
let briefHistory = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadSystemStatus();
    loadExperts();
    setupEventListeners();
    setupSocketListeners();
});

// Initialize application
function initializeApp() {
    // Load saved history from localStorage
    const savedHistory = localStorage.getItem('lexicon_history');
    if (savedHistory) {
        briefHistory = JSON.parse(savedHistory);
        updateHistoryTable();
    }
}

// Load system status
async function loadSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'online') {
            document.getElementById('status-indicator').className = 'badge bg-success';
            document.getElementById('status-indicator').innerHTML = '<i class="fas fa-circle"></i> Online';
            document.getElementById('vector-count').textContent = data.corpus_vectors.toLocaleString();
        } else {
            document.getElementById('status-indicator').className = 'badge bg-danger';
            document.getElementById('status-indicator').innerHTML = '<i class="fas fa-circle"></i> Offline';
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Load expert list
async function loadExperts() {
    try {
        const response = await fetch('/api/experts');
        const data = await response.json();
        
        if (data.success) {
            const expertList = document.getElementById('expert-list');
            expertList.innerHTML = '';
            
            data.experts.forEach(expert => {
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'list-group-item list-group-item-action small';
                item.textContent = expert;
                item.onclick = (e) => {
                    e.preventDefault();
                    selectExpert(expert);
                };
                expertList.appendChild(item);
            });
            
            // Also update the filter dropdown
            const filterSelect = document.getElementById('filter-expert');
            filterSelect.innerHTML = '<option value="">All Experts</option>';
            data.experts.forEach(expert => {
                const option = document.createElement('option');
                option.value = expert;
                option.textContent = expert;
                filterSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading experts:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(link.dataset.tab);
        });
    });
    
    // Search form
    document.getElementById('search-form').addEventListener('submit', handleSearch);
    
    // Generate form
    document.getElementById('generate-form').addEventListener('submit', handleGenerate);
    
    // Strategy change
    document.getElementById('strategy').addEventListener('change', updateMotionTypes);
    
    // File input
    document.getElementById('file-input').addEventListener('change', handleFileSelect);
    
    // Upload form
    document.getElementById('upload-form').addEventListener('submit', handleUpload);
}

// Setup Socket.IO listeners
function setupSocketListeners() {
    socket.on('connected', (data) => {
        console.log('Connected to LEXICON:', data.message);
    });
    
    socket.on('brief_progress', (data) => {
        if (data.task_id === currentBriefTask) {
            updateBriefProgress(data.stage, data.progress);
        }
    });
    
    socket.on('brief_complete', (data) => {
        if (data.task_id === currentBriefTask) {
            handleBriefComplete(data);
        }
    });
    
    socket.on('processing_progress', (data) => {
        if (data.task_id === currentProcessTask) {
            updateProcessingProgress(data.stage, data.progress);
        }
    });
    
    socket.on('processing_complete', (data) => {
        if (data.task_id === currentProcessTask) {
            handleProcessingComplete(data);
        }
    });
}

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).style.display = 'block';
    
    // Update active state
    document.querySelectorAll('[data-tab]').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.tab === tabName) {
            link.classList.add('active');
        }
    });
}

// Search handling
async function handleSearch(e) {
    e.preventDefault();
    
    const query = document.getElementById('search-query').value;
    const expert = document.getElementById('filter-expert').value;
    const docType = document.getElementById('filter-doctype').value;
    const resultCount = document.getElementById('result-count').value || 10;
    
    if (!query) {
        alert('Please enter search terms');
        return;
    }
    
    // Show loading
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border"></div> Searching...</div>';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                query: query,
                n_results: parseInt(resultCount),
                filters: {
                    expert_name: expert,
                    document_type: docType
                }
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">Search failed: ${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Display search results
function displaySearchResults(results) {
    const resultsDiv = document.getElementById('search-results');
    
    if (results.length === 0) {
        resultsDiv.innerHTML = '<div class="alert alert-info">No results found</div>';
        return;
    }
    
    let html = `<h5>Found ${results.length} results:</h5>`;
    
    results.forEach((result, index) => {
        const metadata = result.metadata;
        const relevance = result.distance ? (1 - result.distance).toFixed(3) : 'N/A';
        
        html += `
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-title">
                        ${metadata.source_file || 'Unknown File'}
                        <span class="badge bg-info float-end">Relevance: ${relevance}</span>
                    </h6>
                    <div class="row mb-2">
                        <div class="col-md-4">
                            <small class="text-muted">Expert:</small> ${metadata.expert_name || 'N/A'}
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted">Type:</small> ${metadata.document_type || 'N/A'}
                        </div>
                        <div class="col-md-4">
                            <small class="text-muted">Date:</small> ${metadata.document_date || 'N/A'}
                        </div>
                    </div>
                    <p class="card-text small">${result.content}</p>
                    ${metadata.key_findings ? `
                        <p class="mb-0"><small class="text-muted">Key Findings:</small></p>
                        <p class="small">${metadata.key_findings}</p>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// Select expert for brief generation
function selectExpert(expertName) {
    document.getElementById('expert-name').value = expertName;
    switchTab('generate');
}

// Update motion types based on strategy
function updateMotionTypes() {
    const strategy = document.getElementById('strategy').value;
    const motionSelect = document.getElementById('motion-type');
    
    motionSelect.innerHTML = '<option value="">Select motion type...</option>';
    
    if (strategy === 'challenge') {
        motionSelect.innerHTML += `
            <option value="Daubert Motion to Exclude Expert Testimony">Daubert Motion to Exclude</option>
            <option value="Motion in Limine to Exclude Expert">Motion in Limine</option>
            <option value="Motion to Strike Expert Testimony">Motion to Strike</option>
        `;
    } else if (strategy === 'support') {
        motionSelect.innerHTML += `
            <option value="Response to Defendant's Daubert Motion">Response to Daubert Motion</option>
            <option value="Response to Motion in Limine">Response to Motion in Limine</option>
            <option value="Motion to Qualify Expert Witness">Motion to Qualify Expert</option>
        `;
    }
}

// Handle brief generation
async function handleGenerate(e) {
    e.preventDefault();
    
    const expertName = document.getElementById('expert-name').value;
    const strategy = document.getElementById('strategy').value;
    const motionType = document.getElementById('motion-type').value;
    
    if (!expertName || !strategy || !motionType) {
        alert('Please fill in all fields');
        return;
    }
    
    // Hide result, show progress
    document.getElementById('generation-result').style.display = 'none';
    document.getElementById('generation-progress').style.display = 'block';
    updateBriefProgress('Initializing', 0);
    
    try {
        const response = await fetch('/api/generate-brief', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                expert_name: expertName,
                strategy: strategy,
                motion_type: motionType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentBriefTask = data.task_id;
        } else {
            alert('Failed to start brief generation: ' + data.error);
            document.getElementById('generation-progress').style.display = 'none';
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('generation-progress').style.display = 'none';
    }
}

// Update brief generation progress
function updateBriefProgress(stage, progress) {
    const progressBar = document.querySelector('#generation-progress .progress-bar');
    const progressStage = document.getElementById('progress-stage');
    
    progressBar.style.width = progress + '%';
    progressStage.textContent = stage;
}

// Handle brief completion
function handleBriefComplete(data) {
    document.getElementById('generation-progress').style.display = 'none';
    
    if (data.success) {
        // Show result
        document.getElementById('generation-result').style.display = 'block';
        
        // Store filename for download
        document.getElementById('download-brief').dataset.filename = data.filename;
        document.getElementById('modal-download').dataset.filename = data.filename;
        
        // Show brief excerpt in modal
        document.getElementById('brief-preview').textContent = data.brief_excerpt;
        
        // Show metadata
        const metadata = data.full_result;
        document.getElementById('brief-metadata').innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h6>Brief Details:</h6>
                    <ul class="mb-0">
                        <li>Expert: ${metadata.expert}</li>
                        <li>Strategy: ${metadata.strategy}</li>
                        <li>Motion Type: ${metadata.motion_type}</li>
                        <li>Length: ${metadata.length.toLocaleString()} characters</li>
                        <li>Generated: ${new Date(metadata.timestamp).toLocaleString()}</li>
                    </ul>
                </div>
            </div>
        `;
        
        // Add to history
        addToHistory(metadata);
        
        // Setup download buttons
        document.getElementById('download-brief').onclick = () => downloadBrief(data.filename);
        document.getElementById('modal-download').onclick = () => downloadBrief(data.filename);
    } else {
        alert('Brief generation failed: ' + data.error);
    }
}

// Download brief
function downloadBrief(filename) {
    window.location.href = `/api/download-brief/${filename}`;
}

// Add to history
function addToHistory(briefData) {
    briefHistory.unshift({
        ...briefData,
        date: new Date().toISOString()
    });
    
    // Keep only last 50 items
    briefHistory = briefHistory.slice(0, 50);
    
    // Save to localStorage
    localStorage.setItem('lexicon_history', JSON.stringify(briefHistory));
    
    // Update table
    updateHistoryTable();
}

// Update history table
function updateHistoryTable() {
    const tbody = document.getElementById('history-table');
    
    if (briefHistory.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No briefs generated yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = briefHistory.map(item => `
        <tr>
            <td>${new Date(item.date).toLocaleDateString()}</td>
            <td>${item.expert}</td>
            <td><span class="badge bg-${item.strategy === 'support' ? 'success' : 'danger'}">${item.strategy}</span></td>
            <td>${item.motion_type}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewHistoryItem('${item.date}')">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// File handling
function handleFileSelect(e) {
    const files = e.target.files;
    const fileList = document.getElementById('file-list');
    const submitBtn = document.querySelector('#upload-form button[type="submit"]');
    
    if (files.length > 0) {
        let html = '<h6>Selected Files:</h6><ul>';
        for (let file of files) {
            html += `<li>${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</li>`;
        }
        html += '</ul>';
        fileList.innerHTML = html;
        submitBtn.disabled = false;
    } else {
        fileList.innerHTML = '';
        submitBtn.disabled = true;
    }
}

// Handle upload
async function handleUpload(e) {
    e.preventDefault();
    
    const files = document.getElementById('file-input').files;
    if (files.length === 0) return;
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    // Show progress
    document.getElementById('upload-progress').style.display = 'block';
    updateUploadProgress(0, 'Uploading files...');
    
    try {
        const response = await fetch('/api/upload-documents', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentProcessTask = data.task_id;
            updateUploadProgress(50, 'Processing documents...');
        } else {
            alert('Upload failed: ' + data.error);
            document.getElementById('upload-progress').style.display = 'none';
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('upload-progress').style.display = 'none';
    }
}

// Update upload progress
function updateUploadProgress(percent, status) {
    const progressBar = document.querySelector('#upload-progress .progress-bar');
    progressBar.style.width = percent + '%';
    document.getElementById('upload-status').textContent = status;
}

// Handle processing complete
function handleProcessingComplete(data) {
    document.getElementById('upload-progress').style.display = 'none';
    
    if (data.success) {
        alert(`Processing complete!\n\nProcessed: ${data.summary.successfully_processed}\nFailed: ${data.summary.failed}\nVectors created: ${data.summary.total_vectors_created}`);
        
        // Reset form
        document.getElementById('upload-form').reset();
        document.getElementById('file-list').innerHTML = '';
        document.querySelector('#upload-form button[type="submit"]').disabled = true;
        
        // Reload experts and status
        loadExperts();
        loadSystemStatus();
    } else {
        alert('Processing failed: ' + data.error);
    }
}
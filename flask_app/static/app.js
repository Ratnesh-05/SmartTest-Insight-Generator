// Perf Pulse - Simple JavaScript for Flask Interface

document.addEventListener('DOMContentLoaded', function() {
    console.log('Perf Pulse loaded!');
    setupFileUploads();
    setupNavigation();
});

function setupFileUploads() {
    // Performance data file upload
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    
    if (fileInput && uploadArea) {
        // Click to upload
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        // File selected
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0], 'performance');
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0], 'performance');
            }
        });
    }
    
    // Log file upload
    const logFileInput = document.getElementById('logFileInput');
    const logUploadArea = document.getElementById('logUploadArea');
    
    if (logFileInput && logUploadArea) {
        logUploadArea.addEventListener('click', function() {
            logFileInput.click();
        });
        
        logFileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0], 'log');
            }
        });
    }
    
    // Report file upload
    const reportFileInput = document.getElementById('reportFileInput');
    const reportUploadArea = document.getElementById('reportUploadArea');
    
    if (reportFileInput && reportUploadArea) {
        reportUploadArea.addEventListener('click', function() {
            reportFileInput.click();
        });
        
        reportFileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleReportFileUpload(e.target.files[0]);
            }
        });
    }
    
    // Comparison file uploads
    const comparisonFileInputA = document.getElementById('comparisonFileInputA');
    const comparisonFileInputB = document.getElementById('comparisonFileInputB');
    const comparisonUploadAreaA = document.getElementById('comparisonUploadAreaA');
    const comparisonUploadAreaB = document.getElementById('comparisonUploadAreaB');
    
    if (comparisonFileInputA && comparisonUploadAreaA) {
        comparisonUploadAreaA.addEventListener('click', function() {
            comparisonFileInputA.click();
        });
        
        comparisonFileInputA.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleComparisonFileUpload(e.target.files[0], 'A');
            }
        });
    }
    
    if (comparisonFileInputB && comparisonUploadAreaB) {
        comparisonUploadAreaB.addEventListener('click', function() {
            comparisonFileInputB.click();
        });
        
        comparisonFileInputB.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleComparisonFileUpload(e.target.files[0], 'B');
            }
        });
    }
}

function handleFileUpload(file, type) {
    console.log('Uploading file:', file.name, 'Type:', type);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading
    showLoading();
    
    // Upload to Flask API
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            showSuccess('File uploaded successfully!');
            displayResults(data.data, type);
        } else {
            showError(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Upload failed: ' + error.message);
        console.error('Upload error:', error);
    });
}

function handleReportFileUpload(file) {
    console.log('Uploading file for report:', file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show report upload status
    const uploadStatus = document.getElementById('reportUploadStatus');
    const uploadMessage = document.getElementById('reportUploadMessage');
    const generateBtn = document.getElementById('generateReportBtn');
    
    uploadStatus.style.display = 'block';
    uploadMessage.textContent = 'Processing data for report generation...';
    
    // Upload to Flask API
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        uploadStatus.style.display = 'none';
        
        if (data.success) {
            showSuccess('Data uploaded successfully for report generation!');
            
            // Store the data for report generation
            window.reportData = data.data;
            
            // Enable report generation button
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-download me-2"></i>Generate Report';
            
            // Update status
            const statusText = document.querySelector('#reports .text-muted');
            if (statusText) {
                statusText.textContent = `Data ready: ${data.data.total_records} records loaded`;
            }
        } else {
            showError(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        uploadStatus.style.display = 'none';
        showError('Upload failed: ' + error.message);
        console.error('Upload error:', error);
    });
}

function handleComparisonFileUpload(file, testType) {
    console.log(`Uploading comparison file ${testType}:`, file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show status
    const statusElement = document.getElementById(`comparisonStatus${testType}`);
    statusElement.style.display = 'block';
    statusElement.innerHTML = '<small class="text-info">⏳ Processing...</small>';
    
    // Upload to Flask API
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Store comparison data
            if (!window.comparisonData) {
                window.comparisonData = {};
            }
            window.comparisonData[testType] = data.data;
            
            statusElement.innerHTML = `<small class="text-success">✅ File ${testType} loaded (${data.data.total_records} records)</small>`;
            
            // Enable comparison button if both files are loaded
            checkComparisonReady();
        } else {
            statusElement.innerHTML = `<small class="text-danger">❌ Upload failed</small>`;
            showError(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        statusElement.innerHTML = `<small class="text-danger">❌ Upload failed</small>`;
        showError('Upload failed: ' + error.message);
        console.error('Upload error:', error);
    });
}

function checkComparisonReady() {
    const generateComparisonBtn = document.getElementById('generateComparisonBtn');
    if (window.comparisonData && window.comparisonData.A && window.comparisonData.B) {
        generateComparisonBtn.disabled = false;
        generateComparisonBtn.innerHTML = '<i class="fas fa-chart-line me-2"></i>Generate Comparison Report';
    }
}

function generateComparisonReport() {
    if (!window.comparisonData || !window.comparisonData.A || !window.comparisonData.B) {
        showError('Please upload both test files for comparison');
        return;
    }
    
    showLoading('Generating comparison report...');
    
    fetch('/api/reports/comparison', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            testA: window.comparisonData.A,
            testB: window.comparisonData.B
        })
    })
    .then(response => response.blob())
    .then(data => {
        hideLoading();
        
        // Download comparison report
        const url = window.URL.createObjectURL(data);
        const a = document.createElement('a');
        a.href = url;
        a.download = `perf_pulse_comparison_report_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showSuccess('Comparison report generated successfully!');
    })
    .catch(error => {
        hideLoading();
        showError('Comparison report generation failed: ' + error.message);
    });
}

function displayResults(data, type) {
    if (type === 'performance') {
        const resultsDiv = document.getElementById('analysisResults');
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
            
            // Display metrics
            if (data.metrics) {
                displayMetrics(data.metrics);
            }
            
            // Display charts
            if (data.preview && data.preview.length > 0) {
                displayCharts(data.preview);
            }
        }
    } else if (type === 'log') {
        const resultsDiv = document.getElementById('logAnalysisResults');
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
            showInfo('Log analysis completed!');
        }
    }
}

function displayMetrics(metrics) {
    // Update dashboard metrics
    if (metrics.response_time) {
        updateMetric('avgResponseTime', metrics.response_time.mean + 'ms');
        updateMetric('p95ResponseTime', metrics.response_time.p95 + 'ms');
        updateMetric('maxResponseTime', metrics.response_time.max + 'ms');
    }
    
    if (metrics.errors) {
        updateMetric('totalRequests', metrics.errors.total_requests);
        updateMetric('errorRate', metrics.errors.error_rate + '%');
    }
}

function displayCharts(data) {
    // Simple chart display using Plotly
    if (typeof Plotly !== 'undefined' && data.length > 0) {
        const responseTimes = data.map(item => item.response_time || 0);
        const labels = data.map((_, i) => `Request ${i + 1}`);
        
        const trace = {
            x: labels,
            y: responseTimes,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Response Time',
            line: { color: '#667eea' }
        };
        
        const layout = {
            title: 'Response Time Analysis',
            xaxis: { title: 'Request' },
            yaxis: { title: 'Response Time (ms)' }
        };
        
        Plotly.newPlot('responseTimeAnalysis', [trace], layout);
    }
}

function updateMetric(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function setupNavigation() {
    // Tab navigation
    const navLinks = document.querySelectorAll('[data-bs-toggle="tab"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all tabs
            navLinks.forEach(l => l.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
        });
    });
}

function generateReport() {
    if (!window.reportData) {
        showError('Please upload data first before generating a report');
        return;
    }
    
    const reportType = document.getElementById('reportType').value;
    const reportFormat = document.getElementById('reportFormat').value;
    
    showLoading('Generating report...');
    
    fetch('/api/reports/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type: reportType,
            format: reportFormat,
            data: window.reportData
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (reportFormat === 'html') {
            return response.json();
        } else {
            return response.blob();
        }
    })
    .then(data => {
        hideLoading();
        
        if (reportFormat === 'html') {
            // Display HTML report
            if (data.success) {
                showSuccess('HTML report generated!');
                // Show HTML content in new window
                const newWindow = window.open('', '_blank');
                newWindow.document.write(data.html_content);
                newWindow.document.close();
            } else {
                showError(data.error || 'HTML report generation failed');
            }
        } else {
            // Download file
            console.log('Downloading file, size:', data.size);
            const url = window.URL.createObjectURL(data);
            const a = document.createElement('a');
            a.href = url;
            a.download = `perf_pulse_report.${reportFormat}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showSuccess('Report downloaded successfully!');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Report generation failed: ' + error.message);
    });
}

function saveSettings() {
    const settings = {
        warningRT: document.getElementById('warningRT').value,
        criticalRT: document.getElementById('criticalRT').value,
        warningError: document.getElementById('warningError').value,
        criticalError: document.getElementById('criticalError').value
    };
    
    // Save to localStorage for now
    localStorage.setItem('perfPulseSettings', JSON.stringify(settings));
    showSuccess('Settings saved successfully!');
}

// Utility functions
function showLoading(message = 'Loading...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">${message}</p>
        </div>
    `;
    loadingDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    document.body.appendChild(loadingDiv);
}

function hideLoading() {
    const loadingDiv = document.querySelector('.loading-overlay');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showInfo(message) {
    showAlert(message, 'info');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global functions for onclick handlers
window.generateReport = generateReport;
window.saveSettings = saveSettings;
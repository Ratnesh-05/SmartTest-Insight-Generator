// Perf Pulse - Smart Test Insight Generator JavaScript

// Global variables
let currentData = null;
let charts = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupNavigation();
    setupFileUpload();
    setupCharts();
    loadDashboard();
}

// Navigation functionality
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding section
            const targetSection = this.getAttribute('data-section');
            showSection(targetSection);
        });
    });
}

function showSection(sectionName) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('fade-in');
    }
}

// File upload functionality
function setupFileUpload() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('.file-input');
    
    if (uploadArea && fileInput) {
        // Drag and drop events
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
                handleFileUpload(files[0]);
            }
        });
        
        // Click to upload
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }
}

function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading state
    showLoading('Processing file...');
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            currentData = data.data;
            showSuccess('File uploaded successfully!');
            updateDashboard(data.metrics);
            updateCharts(data.data);
            showSection('analysis');
        } else {
            showError(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Upload failed: ' + error.message);
    });
}

// Charts functionality
function setupCharts() {
    // Initialize Chart.js if available
    if (typeof Chart !== 'undefined') {
        setupResponseTimeChart();
        setupThroughputChart();
        setupErrorChart();
    }
}

function setupResponseTimeChart() {
    const ctx = document.getElementById('responseTimeChart');
    if (ctx) {
        charts.responseTime = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Response Time Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function setupThroughputChart() {
    const ctx = document.getElementById('throughputChart');
    if (ctx) {
        charts.throughput = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Requests per Second',
                    data: [],
                    backgroundColor: '#28a745'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Throughput Analysis'
                    }
                }
            }
        });
    }
}

function setupErrorChart() {
    const ctx = document.getElementById('errorChart');
    if (ctx) {
        charts.error = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Success', 'Errors'],
                datasets: [{
                    data: [0, 0],
                    backgroundColor: ['#28a745', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Success vs Error Rate'
                    }
                }
            }
        });
    }
}

function updateCharts(data) {
    if (!data || !data.length) return;
    
    // Update response time chart
    if (charts.responseTime && data.some(d => d.response_time)) {
        const responseTimes = data.map(d => d.response_time);
        const labels = data.map((_, i) => `Request ${i + 1}`);
        
        charts.responseTime.data.labels = labels;
        charts.responseTime.data.datasets[0].data = responseTimes;
        charts.responseTime.update();
    }
    
    // Update error chart
    if (charts.error) {
        const total = data.length;
        const errors = data.filter(d => d.status_code >= 400).length;
        const success = total - errors;
        
        charts.error.data.datasets[0].data = [success, errors];
        charts.error.update();
    }
}

// Dashboard functionality
function loadDashboard() {
    fetch('/api/dashboard')
    .then(response => response.json())
    .then(data => {
        updateDashboard(data);
    })
    .catch(error => {
        console.error('Error loading dashboard:', error);
    });
}

function updateDashboard(metrics) {
    // Update metric cards
    if (metrics.response_time) {
        updateMetricCard('avgResponseTime', metrics.response_time.mean, 'ms');
        updateMetricCard('p95ResponseTime', metrics.response_time.p95, 'ms');
        updateMetricCard('maxResponseTime', metrics.response_time.max, 'ms');
    }
    
    if (metrics.errors) {
        updateMetricCard('totalRequests', metrics.errors.total_requests, '');
        updateMetricCard('errorRate', metrics.errors.error_rate, '%');
    }
}

function updateMetricCard(id, value, unit) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value.toFixed(2) + unit;
    }
}

// Report generation
function generateReport(format) {
    if (!currentData) {
        showError('No data available for report generation');
        return;
    }
    
    showLoading('Generating report...');
    
    fetch('/api/generate-report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            format: format,
            data: currentData
        })
    })
    .then(response => response.blob())
    .then(blob => {
        hideLoading();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `perf_pulse_report_${new Date().toISOString().slice(0, 10)}.${format.toLowerCase()}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showSuccess('Report generated successfully!');
    })
    .catch(error => {
        hideLoading();
        showError('Report generation failed: ' + error.message);
    });
}

// Utility functions
function showLoading(message = 'Loading...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = `
        <div class="loading-content">
            <div class="spinner"></div>
            <p>${message}</p>
        </div>
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

function showWarning(message) {
    showAlert(message, 'warning');
}

function showInfo(message) {
    showAlert(message, 'info');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Real-time updates
function startRealTimeUpdates() {
    setInterval(() => {
        if (currentData) {
            fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                updateRealTimeMetrics(data);
            })
            .catch(error => {
                console.error('Error updating real-time metrics:', error);
            });
        }
    }, 5000); // Update every 5 seconds
}

function updateRealTimeMetrics(data) {
    // Update real-time metrics if available
    if (data.current_requests) {
        updateMetricCard('currentRequests', data.current_requests, '');
    }
    
    if (data.current_response_time) {
        updateMetricCard('currentResponseTime', data.current_response_time, 'ms');
    }
}

// Initialize real-time updates
startRealTimeUpdates();

// Export functions for global access
window.PerfPulse = {
    generateReport,
    showSection,
    handleFileUpload,
    updateDashboard,
    updateCharts
};
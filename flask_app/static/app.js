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
            file_a_path: window.comparisonData.A.file_path,
            file_b_path: window.comparisonData.B.file_path,
            format: 'pdf'
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Comparison report generation failed');
            });
        }
        return response.blob();
    })
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
    const chartsContainer = document.getElementById('chartsContainer');
    if (!chartsContainer) return;
    
    chartsContainer.innerHTML = '<h3>🚀 Advanced Performance Visualizations</h3>';
    
    if (data && data.charts) {
        // Create interactive chart tabs
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'chart-tabs';
        tabsContainer.innerHTML = `
            <div class="tab-buttons">
                ${Object.keys(data.charts).map((chartName, index) => 
                    `<button class="tab-button ${index === 0 ? 'active' : ''}" onclick="showChart('${chartName}', this)">
                        ${formatChartName(chartName)}
                    </button>`
                ).join('')}
            </div>
            <div class="tab-content">
                ${Object.keys(data.charts).map((chartName, index) => 
                    `<div id="chart-${chartName}" class="chart-container" style="display: ${index === 0 ? 'block' : 'none'}">
                        <div class="chart-loading">🎨 Loading beautiful chart...</div>
                    </div>`
                ).join('')}
            </div>
        `;
        
        chartsContainer.appendChild(tabsContainer);
        
        // Render all charts
        Object.entries(data.charts).forEach(([chartName, chartData], index) => {
            setTimeout(() => {
                renderEnhancedChart(chartName, chartData, document.getElementById(`chart-${chartName}`));
            }, index * 500);
        });
    } else if (data && data.length > 0) {
        // Fallback to simple chart
        renderSimpleChart(data, chartsContainer);
    }
}

function formatChartName(name) {
    const icons = {
        'response_time_distribution': '📊',
        'response_time_trend': '📈',
        'error_analysis': '❌',
        'performance_gauges': '🎯',
        'throughput_analysis': '⚡',
        'anomaly_detection': '🔍',
        'performance_heatmap': '🔥',
        'performance_trends': '📉',
        'percentile_analysis': '📋'
    };
    
    const icon = icons[name] || '📊';
    const formattedName = name.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
    
    return `${icon} ${formattedName}`;
}

function showChart(chartName, button) {
    // Update active tab
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    // Show selected chart
    document.querySelectorAll('.chart-container').forEach(container => {
        container.style.display = 'none';
    });
    document.getElementById(`chart-${chartName}`).style.display = 'block';
}

function renderEnhancedChart(chartName, chartData, container) {
    // Add beautiful loading animation
    container.innerHTML = `
        <div class="chart-loading">
            <div class="loading-spinner"></div>
            <p>🎨 Creating beautiful visualization...</p>
        </div>
    `;
    
    setTimeout(() => {
        if (chartData.type === 'histogram') {
            renderHistogramChart(chartData, container);
        } else if (chartData.type === 'scatter') {
            renderScatterChart(chartData, container);
        } else if (chartData.type === 'pie') {
            renderPieChart(chartData, container);
        } else if (chartData.type === 'bar') {
            renderBarChart(chartData, container);
        } else if (chartData.type === 'indicator') {
            renderGaugeChart(chartData, container);
        } else if (chartData.type === 'heatmap') {
            renderHeatmapChart(chartData, container);
        } else if (chartData.type === 'box') {
            renderBoxChart(chartData, container);
        } else {
            renderGenericChart(chartData, container);
        }
    }, 800);
}

function renderHistogramChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    // Create gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#3b82f6');
    gradient.addColorStop(1, '#1d4ed8');
    
    // Animate histogram with beautiful effects
    animateHistogram(ctx, data.data.x, canvas.width, canvas.height, gradient);
}

function renderScatterChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    if (Array.isArray(data.data)) {
        // Multi-line chart with different colors
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
        data.data.forEach((series, index) => {
            setTimeout(() => {
                animateScatterPlot(ctx, series, canvas.width, canvas.height, colors[index % colors.length]);
            }, index * 300);
        });
    } else {
        animateScatterPlot(ctx, data.data, canvas.width, canvas.height, '#3b82f6');
    }
}

function renderPieChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    // Create animated 3D pie chart with beautiful colors
    const colors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];
    animatePieChart(ctx, data.data.labels, data.data.values, canvas.width, canvas.height, colors);
}

function renderBarChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    // Create animated 3D bar chart
    animateBarChart(ctx, data.data.x, data.data.y, canvas.width, canvas.height);
}

function renderGaugeChart(data, container) {
    container.innerHTML = `
        <div class="gauge-container">
            <h4>${data.layout.title.text}</h4>
            <div class="gauge-wrapper">
                <div class="gauge" id="gauge-${Math.random().toString(36).substr(2, 9)}">
                    <div class="gauge-value">0</div>
                    <div class="gauge-label">${data.data.title.text}</div>
                    <div class="gauge-ring"></div>
                </div>
            </div>
        </div>
    `;
    
    // Animate gauge with smooth transitions
    const gaugeElement = container.querySelector('.gauge');
    animateGauge(gaugeElement, data.data.value, data.gauge.axis.range[1]);
}

function renderHeatmapChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    // Create animated heatmap with color gradients
    animateHeatmap(ctx, data.data.z[0], canvas.width, canvas.height);
}

function renderBoxChart(data, container) {
    const canvas = createCanvas(container, data.layout.title.text);
    const ctx = canvas.getContext('2d');
    
    // Create animated box plot
    animateBoxPlot(ctx, data.data.y, canvas.width, canvas.height);
}

function renderGenericChart(data, container) {
    container.innerHTML = `
        <div class="generic-chart">
            <h4>${data.layout.title.text}</h4>
            <div class="chart-placeholder">
                <div class="chart-icon">📊</div>
                <p>Advanced visualization available</p>
                <div class="chart-stats">
                    <div class="stat-item">
                        <span class="stat-value">${data.data.x ? data.data.x.length : 0}</span>
                        <span class="stat-label">Data Points</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderSimpleChart(data, container) {
    container.innerHTML = `
        <div class="simple-chart">
            <h4>📊 Response Time Analysis</h4>
            <div class="chart-placeholder">
                <div class="chart-icon">📈</div>
                <p>Basic chart data available</p>
                <div class="chart-stats">
                    <div class="stat-item">
                        <span class="stat-value">${data.length}</span>
                        <span class="stat-label">Data Points</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function createCanvas(container, title) {
    container.innerHTML = `
        <div class="chart-wrapper">
            <h4>${title}</h4>
            <canvas width="600" height="400"></canvas>
        </div>
    `;
    return container.querySelector('canvas');
}

// Enhanced animation functions with beautiful effects
function animateHistogram(ctx, data, width, height, gradient) {
    const maxValue = Math.max(...data);
    const barWidth = width / 25;
    const barSpacing = 3;
    
    data.forEach((value, index) => {
        const barHeight = (value / maxValue) * (height - 60);
        const x = index * (barWidth + barSpacing) + 20;
        const y = height - barHeight - 30;
        
        setTimeout(() => {
            // Draw bar with gradient
            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Add highlight effect
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fillRect(x, y, barWidth, Math.min(20, barHeight));
            
            // Add border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, barWidth, barHeight);
            
            // Add value label
            ctx.fillStyle = '#1f2937';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(value, x + barWidth / 2, y - 5);
        }, index * 30);
    });
}

function animateScatterPlot(ctx, data, width, height, color) {
    const maxX = Math.max(...data.x);
    const maxY = Math.max(...data.y);
    
    data.x.forEach((x, index) => {
        const canvasX = (x / maxX) * (width - 40) + 20;
        const canvasY = height - ((data.y[index] / maxY) * (height - 40) + 20);
        
        setTimeout(() => {
            // Draw point with glow effect
            ctx.shadowColor = color;
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.arc(canvasX, canvasY, 5, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
            
            // Reset shadow
            ctx.shadowBlur = 0;
            
            // Add border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
        }, index * 20);
    });
}

function animatePieChart(ctx, labels, values, width, height, colors) {
    const total = values.reduce((sum, val) => sum + val, 0);
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;
    
    let currentAngle = 0;
    
    values.forEach((value, index) => {
        const sliceAngle = (value / total) * 2 * Math.PI;
        
        setTimeout(() => {
            // Draw slice with 3D effect
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            ctx.closePath();
            ctx.fillStyle = colors[index % colors.length];
            ctx.fill();
            
            // Add 3D effect
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            // Add label with connector line
            const labelAngle = currentAngle + sliceAngle / 2;
            const labelX = centerX + (radius + 30) * Math.cos(labelAngle);
            const labelY = centerY + (radius + 30) * Math.sin(labelAngle);
            
            // Draw connector line
            ctx.beginPath();
            ctx.moveTo(centerX + radius * Math.cos(labelAngle), centerY + radius * Math.sin(labelAngle));
            ctx.lineTo(labelX, labelY);
            ctx.strokeStyle = '#1f2937';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Add label
            ctx.fillStyle = '#1f2937';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(labels[index], labelX, labelY);
            
            currentAngle += sliceAngle;
        }, index * 300);
    });
}

function animateBarChart(ctx, labels, values, width, height) {
    const maxValue = Math.max(...values);
    const barWidth = width / (labels.length + 2);
    const colors = ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    
    labels.forEach((label, index) => {
        const barHeight = (values[index] / maxValue) * (height - 100);
        const x = (index + 1) * barWidth;
        const y = height - barHeight - 50;
        
        setTimeout(() => {
            // Create 3D bar effect
            const color = colors[index % colors.length];
            
            // Main bar
            ctx.fillStyle = color;
            ctx.fillRect(x, y, barWidth - 10, barHeight);
            
            // Top highlight
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fillRect(x, y, barWidth - 10, 15);
            
            // Side highlight
            ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.fillRect(x, y, 5, barHeight);
            
            // Border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, barWidth - 10, barHeight);
            
            // Labels
            ctx.fillStyle = '#1f2937';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(label, x + (barWidth - 10) / 2, height - 30);
            ctx.fillText(values[index], x + (barWidth - 10) / 2, y - 10);
        }, index * 400);
    });
}

function animateGauge(gaugeElement, value, maxValue) {
    const percentage = (value / maxValue) * 100;
    const gaugeValue = gaugeElement.querySelector('.gauge-value');
    const gaugeRing = gaugeElement.querySelector('.gauge-ring');
    
    let currentValue = 0;
    const increment = value / 100;
    
    const animation = setInterval(() => {
        currentValue += increment;
        if (currentValue >= value) {
            currentValue = value;
            clearInterval(animation);
        }
        
        gaugeValue.textContent = Math.round(currentValue);
        gaugeRing.style.transform = `rotate(${(currentValue / maxValue) * 180}deg)`;
        gaugeRing.style.borderColor = getGaugeColor(percentage);
    }, 20);
}

function animateHeatmap(ctx, data, width, height) {
    const maxValue = Math.max(...data);
    const cellWidth = width / data.length;
    const cellHeight = height;
    
    data.forEach((value, index) => {
        const intensity = value / maxValue;
        const color = getHeatmapColor(intensity);
        
        setTimeout(() => {
            ctx.fillStyle = color;
            ctx.fillRect(index * cellWidth, 0, cellWidth, cellHeight);
            
            // Add value label
            ctx.fillStyle = '#ffffff';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(Math.round(value), index * cellWidth + cellWidth / 2, height / 2);
        }, index * 15);
    });
}

function animateBoxPlot(ctx, data, width, height) {
    const sortedData = data.sort((a, b) => a - b);
    const q1 = sortedData[Math.floor(sortedData.length * 0.25)];
    const q2 = sortedData[Math.floor(sortedData.length * 0.5)];
    const q3 = sortedData[Math.floor(sortedData.length * 0.75)];
    const min = sortedData[0];
    const max = sortedData[sortedData.length - 1];
    
    const boxWidth = 120;
    const boxX = width / 2 - boxWidth / 2;
    const boxY = height / 2 - 60;
    
    // Animate box plot drawing
    setTimeout(() => {
        // Whiskers
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(boxX + boxWidth / 2, boxY + 20);
        ctx.lineTo(boxX + boxWidth / 2, boxY + 40);
        ctx.moveTo(boxX, boxY + 40);
        ctx.lineTo(boxX + boxWidth, boxY + 40);
        ctx.stroke();
        
        // Box with gradient
        const gradient = ctx.createLinearGradient(boxX, boxY, boxX + boxWidth, boxY);
        gradient.addColorStop(0, '#8b5cf6');
        gradient.addColorStop(1, '#a855f7');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(boxX, boxY + 20, boxWidth, 20);
        ctx.strokeRect(boxX, boxY + 20, boxWidth, 20);
        
        // Median line
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(boxX, boxY + 30);
        ctx.lineTo(boxX + boxWidth, boxY + 30);
        ctx.stroke();
        
        // Add statistics
        ctx.fillStyle = '#1f2937';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Q1: ${Math.round(q1)}`, boxX + boxWidth / 4, boxY + 10);
        ctx.fillText(`Q2: ${Math.round(q2)}`, boxX + boxWidth / 2, boxY + 10);
        ctx.fillText(`Q3: ${Math.round(q3)}`, boxX + 3 * boxWidth / 4, boxY + 10);
    }, 500);
}

function getGaugeColor(percentage) {
    if (percentage < 30) return '#10b981';
    if (percentage < 70) return '#f59e0b';
    return '#ef4444';
}

function getHeatmapColor(intensity) {
    const r = Math.round(59 + (196 - 59) * intensity);
    const g = Math.round(130 + (196 - 130) * intensity);
    const b = Math.round(246 + (196 - 246) * intensity);
    return `rgb(${r}, ${g}, ${b})`;
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
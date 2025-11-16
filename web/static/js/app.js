/**
 * MediFlow Web Interface JavaScript
 */

const API_BASE = 'http://localhost:5000/api';

// View navigation
function showView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.style.display = 'none';
    });
    document.getElementById(viewId).style.display = 'block';
    
    // Update active nav item
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
}

function showSimulator() {
    showView('simulator-view');
}

function showOptimizer() {
    showView('optimizer-view');
}

function showResults() {
    showView('results-view');
    loadResultsList();
}

// Simulator functionality
document.getElementById('simulator-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const params = {
        arrival_rate: parseFloat(document.getElementById('arrival_rate').value),
        service_rate: parseFloat(document.getElementById('service_rate').value),
        servers: parseInt(document.getElementById('servers').value),
        hours: parseFloat(document.getElementById('hours').value),
        seed: parseInt(document.getElementById('seed').value) || 42,
        export: true
    };
    
    // Show loading
    document.getElementById('simulator-loading').style.display = 'block';
    document.getElementById('simulator-results').style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/simulate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displaySimulationResults(data.results);
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Failed to run simulation: ' + error.message);
    } finally {
        document.getElementById('simulator-loading').style.display = 'none';
    }
});

function displaySimulationResults(results) {
    document.getElementById('result-patients').textContent = results.patients_served;
    document.getElementById('result-wait').textContent = results.avg_wait_time.toFixed(4) + ' hrs';
    document.getElementById('result-queue').textContent = results.avg_queue_length.toFixed(2);
    document.getElementById('result-util').textContent = (results.utilization * 100).toFixed(1) + '%';
    
    // Status message
    const statusDiv = document.getElementById('result-status');
    statusDiv.textContent = results.system_status;
    
    if (results.system_status.includes('Unstable')) {
        statusDiv.className = 'alert alert-danger';
    } else if (results.system_status.includes('High')) {
        statusDiv.className = 'alert alert-warning';
    } else {
        statusDiv.className = 'alert alert-success';
    }
    
    document.getElementById('simulator-results').style.display = 'block';
}

// Optimizer functionality
async function runOptimization() {
    document.getElementById('optimizer-loading').style.display = 'block';
    document.getElementById('optimizer-results').style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ export: true })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayOptimizationResults(data.results);
        } else {
            alert('Error: ' + (data.message || data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Failed to run optimization: ' + error.message);
    } finally {
        document.getElementById('optimizer-loading').style.display = 'none';
    }
}

function displayOptimizationResults(results) {
    document.getElementById('opt-cost').textContent = results.total_cost.toFixed(2);
    
    // Populate assignments table
    const tbody = document.querySelector('#opt-assignments-table tbody');
    tbody.innerHTML = '';
    
    for (const [staff, data] of Object.entries(results.assignments)) {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = staff;
        row.insertCell(1).textContent = data.shifts.join(', ') || '-';
        row.insertCell(2).textContent = data.hours;
    }
    
    document.getElementById('optimizer-results').style.display = 'block';
}

// Results list functionality
async function loadResultsList() {
    try {
        const response = await fetch(`${API_BASE}/results`);
        const data = await response.json();
        
        const resultsDiv = document.getElementById('results-list');
        
        if (data.files.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No saved results yet.</p>';
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table table-hover"><thead><tr><th>Type</th><th>ID</th><th>Date</th><th>Actions</th></tr></thead><tbody>';
        
        data.files.forEach(file => {
            const type = file.type.charAt(0).toUpperCase() + file.type.slice(1);
            const date = new Date(file.modified).toLocaleString();
            const badge = file.type === 'simulation' ? 'badge bg-primary' : 'badge bg-success';
            
            html += `
                <tr>
                    <td><span class="${badge}">${type}</span></td>
                    <td><code>${file.id}</code></td>
                    <td>${date}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewResult('${file.id}')">
                            <i class="bi bi-eye"></i> View
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        resultsDiv.innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load results:', error);
    }
}

async function viewResult(id) {
    try {
        const response = await fetch(`${API_BASE}/results/${id}`);
        const data = await response.json();
        
        // Display in a modal or new view
        alert('Result data:\n' + JSON.stringify(data, null, 2));
    } catch (error) {
        alert('Failed to load result: ' + error.message);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('MediFlow Web Interface loaded');
});

/**
 * MediFlow Web Interface - Modern JavaScript
 */

// Dynamically detect API base URL (works with any port)
const API_BASE = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/api`;

// View navigation with smooth transitions
function showView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.style.display = 'none';
    });
    
    const targetView = document.getElementById(viewId);
    targetView.style.display = 'block';
    
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateActiveNav(element) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    }
}

function showDashboard(e) {
    if (e) {
        e.preventDefault();
        updateActiveNav(e.currentTarget);
    }
    showView('dashboard-view');
}

function showSimulator(e) {
    if (e) {
        e.preventDefault();
        updateActiveNav(e.currentTarget);
    }
    showView('simulator-view');
}

function showOptimizer(e) {
    if (e) {
        e.preventDefault();
        updateActiveNav(e.currentTarget);
    }
    showView('optimizer-view');
    loadConfig();
}

function showResults(e) {
    if (e) {
        e.preventDefault();
        updateActiveNav(e.currentTarget);
    }
    showView('results-view');
    loadResultsList();
}

// Enhanced toast notifications
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    toast.style.cssText = 'z-index: 9999; min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Fade in
    setTimeout(() => toast.style.opacity = '1', 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Simulator functionality with enhanced error handling
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
    
    // Validate inputs
    if (params.arrival_rate <= 0 || params.service_rate <= 0 || params.servers <= 0 || params.hours <= 0) {
        showToast('Please enter valid positive numbers for all parameters', 'danger');
        return;
    }
    
    // Show loading with animation
    const loadingDiv = document.getElementById('simulator-loading');
    const resultsDiv = document.getElementById('simulator-results');
    
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    
    // Disable form during processing
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Running...';
    
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
            showToast('Simulation completed successfully!', 'success');
        } else {
            showToast('Error: ' + (data.error || 'Unknown error'), 'danger');
        }
    } catch (error) {
        showToast('Failed to run simulation: ' + error.message, 'danger');
        console.error('Simulation error:', error);
    } finally {
        loadingDiv.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-play-fill"></i> Run Simulation';
    }
});

function displaySimulationResults(results) {
    // Animate counter updates
    animateValue('result-patients', 0, results.patients_served, 800);
    
    document.getElementById('result-wait').textContent = results.avg_wait_time.toFixed(4) + ' hrs';
    document.getElementById('result-queue').textContent = results.avg_queue_length.toFixed(2);
    document.getElementById('result-util').textContent = (results.utilization * 100).toFixed(1) + '%';
    
    // Status message with enhanced styling
    const statusDiv = document.getElementById('result-status');
    statusDiv.textContent = results.system_status;
    
    // Color code based on status with smooth transitions
    statusDiv.style.opacity = '0';
    
    setTimeout(() => {
        if (results.system_status.includes('🔴') || results.system_status.includes('CRITICAL')) {
            statusDiv.className = 'alert alert-danger';
        } else if (results.system_status.includes('🟠') || results.system_status.includes('WARNING')) {
            statusDiv.className = 'alert alert-warning';
        } else if (results.system_status.includes('🟡') || results.system_status.includes('CAUTION')) {
            statusDiv.className = 'alert alert-info';
        } else {
            statusDiv.className = 'alert alert-success';
        }
        statusDiv.style.opacity = '1';
        statusDiv.style.transition = 'opacity 0.3s ease';
    }, 100);
    
    // Display recommendations with enhanced formatting
    const recommendations = results.recommendations || [];
    if (recommendations.length > 0) {
        const recDiv = document.getElementById('result-recommendations');
        const recList = document.getElementById('recommendations-list');
        recList.innerHTML = '';
        
        recommendations.forEach((rec, index) => {
            const li = document.createElement('li');
            li.textContent = rec;
            li.style.opacity = '0';
            li.style.transform = 'translateX(-10px)';
            recList.appendChild(li);
            
            // Staggered animation
            setTimeout(() => {
                li.style.transition = 'all 0.3s ease';
                li.style.opacity = '1';
                li.style.transform = 'translateX(0)';
            }, 100 + (index * 50));
        });
        
        recDiv.style.display = 'block';
    }
    
    // Show results with animation
    const resultsDiv = document.getElementById('simulator-results');
    resultsDiv.style.opacity = '0';
    resultsDiv.style.display = 'block';
    
    setTimeout(() => {
        resultsDiv.style.transition = 'opacity 0.5s ease';
        resultsDiv.style.opacity = '1';
    }, 50);
}

// Smooth number animation
function animateValue(id, start, end, duration) {
    const element = document.getElementById(id);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// Optimizer functionality with enhanced UX
async function runOptimization() {
    const loadingDiv = document.getElementById('optimizer-loading');
    const resultsDiv = document.getElementById('optimizer-results');
    
    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    
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
            showToast('Optimization completed successfully!', 'success');
        } else {
            showToast('Error: ' + (data.message || data.error || 'Unknown error'), 'danger');
        }
    } catch (error) {
        showToast('Failed to run optimization: ' + error.message, 'danger');
        console.error('Optimization error:', error);
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function displayOptimizationResults(results) {
    // Animate cost display
    animateValue('opt-cost', 0, results.total_cost, 1000);
    
    // Populate assignments table with enhanced styling
    const tbody = document.querySelector('#opt-assignments-table tbody');
    tbody.innerHTML = '';
    
    let rowIndex = 0;
    for (const [staff, data] of Object.entries(results.assignments)) {
        const row = tbody.insertRow();
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';
        
        row.insertCell(0).textContent = staff;
        row.insertCell(1).textContent = data.shifts.join(', ') || '-';
        row.insertCell(2).textContent = data.hours;
        
        // Staggered animation
        setTimeout(() => {
            row.style.transition = 'all 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, rowIndex * 50);
        
        rowIndex++;
    }
    
    // Show results with animation
    const resultsDiv = document.getElementById('optimizer-results');
    resultsDiv.style.opacity = '0';
    resultsDiv.style.display = 'block';
    
    setTimeout(() => {
        resultsDiv.style.transition = 'opacity 0.5s ease';
        resultsDiv.style.opacity = '1';
    }, 50);
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

// Initialize with smooth animations
document.addEventListener('DOMContentLoaded', () => {
    console.log('%c🏥 MediFlow Suite Loaded', 'color: #2563eb; font-size: 16px; font-weight: bold;');
    console.log('%cHealthcare Optimization Platform v2.0', 'color: #666; font-size: 12px;');
    
    // Add fade-in animation to initial view
    const dashboardView = document.getElementById('dashboard-view');
    if (dashboardView) {
        dashboardView.style.opacity = '0';
        setTimeout(() => {
            dashboardView.style.transition = 'opacity 0.5s ease';
            dashboardView.style.opacity = '1';
        }, 100);
    }
    
    // Add input validation feedback
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function() {
            if (this.value && parseFloat(this.value) <= 0) {
                this.style.borderColor = 'var(--danger)';
            } else {
                this.style.borderColor = '';
            }
        });
    });
});

// Config management
let currentConfig = null;

async function loadConfig() {
    document.getElementById('config-loading').style.display = 'block';
    document.getElementById('config-editor').style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();
        
        currentConfig = data;
        displayConfigEditor(data.current_loaded);
        
        document.getElementById('config-loading').style.display = 'none';
        document.getElementById('config-editor').style.display = 'block';
    } catch (error) {
        console.error('Failed to load config:', error);
        document.getElementById('config-loading').innerHTML = 
            '<div class="alert alert-danger">Failed to load configuration</div>';
    }
}

function displayConfigEditor(config) {
    // Display staff configuration
    const staffTable = document.querySelector('#staff-config-table tbody');
    staffTable.innerHTML = '';
    
    config.staff.forEach((staff, index) => {
        const row = staffTable.insertRow();
        row.innerHTML = `
            <td><input type="text" class="form-control form-control-sm" value="${staff.name}" data-field="name" data-index="${index}"></td>
            <td><input type="number" class="form-control form-control-sm" value="${staff.cost}" data-field="cost" data-index="${index}" min="0" step="0.5"></td>
            <td><input type="number" class="form-control form-control-sm" value="${staff.max_hours}" data-field="max_hours" data-index="${index}" min="0"></td>
            <td><input type="text" class="form-control form-control-sm" value="${staff.availability.join(', ')}" data-field="availability" data-index="${index}" placeholder="Mon_AM, Tue_AM, ..."></td>
            <td><button class="btn btn-sm btn-danger" onclick="deleteStaffRow(${index})"><i class="bi bi-trash"></i></button></td>
        `;
    });
    
    // Display shift requirements
    const shiftTable = document.querySelector('#shift-requirements-table tbody');
    shiftTable.innerHTML = '';
    
    Object.entries(config.shift_requirements).forEach(([shift, required]) => {
        const row = shiftTable.insertRow();
        row.innerHTML = `
            <td>${shift}</td>
            <td><input type="number" class="form-control form-control-sm" value="${required}" data-shift="${shift}" min="0"></td>
        `;
    });
}

function addStaffRow() {
    const staffTable = document.querySelector('#staff-config-table tbody');
    const index = staffTable.rows.length;
    const row = staffTable.insertRow();
    row.innerHTML = `
        <td><input type="text" class="form-control form-control-sm" value="New_Staff" data-field="name" data-index="${index}"></td>
        <td><input type="number" class="form-control form-control-sm" value="20" data-field="cost" data-index="${index}" min="0" step="0.5"></td>
        <td><input type="number" class="form-control form-control-sm" value="40" data-field="max_hours" data-index="${index}" min="0"></td>
        <td><input type="text" class="form-control form-control-sm" value="Mon_AM, Tue_AM" data-field="availability" data-index="${index}" placeholder="Mon_AM, Tue_AM, ..."></td>
        <td><button class="btn btn-sm btn-danger" onclick="deleteStaffRow(${index})"><i class="bi bi-trash"></i></button></td>
    `;
}

function deleteStaffRow(index) {
    const staffTable = document.querySelector('#staff-config-table tbody');
    if (staffTable.rows.length > 1) {
        staffTable.deleteRow(index);
        // Re-index remaining rows
        Array.from(staffTable.rows).forEach((row, newIndex) => {
            row.querySelectorAll('[data-index]').forEach(input => {
                input.setAttribute('data-index', newIndex);
            });
            const deleteBtn = row.querySelector('button');
            if (deleteBtn) {
                deleteBtn.setAttribute('onclick', `deleteStaffRow(${newIndex})`);
            }
        });
    } else {
        alert('Must have at least one staff member');
    }
}

function collectConfigFromForm() {
    const staffConfig = {};
    const staffTable = document.querySelector('#staff-config-table tbody');
    
    Array.from(staffTable.rows).forEach(row => {
        const inputs = row.querySelectorAll('input');
        const name = inputs[0].value.trim();
        const cost = parseFloat(inputs[1].value);
        const maxHours = parseInt(inputs[2].value);
        const availability = inputs[3].value.split(',').map(s => s.trim()).filter(s => s);
        
        staffConfig[name] = {
            cost: cost,
            max_hours: maxHours,
            availability: availability
        };
    });
    
    const shiftRequirements = {};
    const shiftTable = document.querySelector('#shift-requirements-table tbody');
    
    Array.from(shiftTable.rows).forEach(row => {
        const shift = row.cells[0].textContent;
        const required = parseInt(row.querySelector('input').value);
        shiftRequirements[shift] = required;
    });
    
    return {
        simulator: currentConfig.config_file.simulator,
        optimiser: {
            staff: staffConfig,
            shift_requirements: shiftRequirements,
            shift_duration_hours: 8,
            days: ["Mon", "Tue", "Wed", "Thu", "Fri"],
            times: ["AM", "PM"]
        },
        export: currentConfig.config_file.export,
        logging: currentConfig.config_file.logging
    };
}

async function saveAndRunOptimization() {
    const newConfig = collectConfigFromForm();
    
    const loadingDiv = document.getElementById('config-loading');
    loadingDiv.style.display = 'block';
    loadingDiv.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div><span class="ms-2">Saving configuration...</span></div>';
    
    try {
        // Save config
        const saveResponse = await fetch(`${API_BASE}/config`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newConfig)
        });
        
        if (!saveResponse.ok) {
            throw new Error('Failed to save configuration');
        }
        
        showToast('Configuration saved successfully!', 'success');
        
        // Run optimization
        loadingDiv.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div><span class="ms-2">Running optimization...</span></div>';
        await runOptimization();
        
    } catch (error) {
        showToast('Error: ' + error.message, 'danger');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

async function testConfiguration() {
    const newConfig = collectConfigFromForm();
    
    const loadingDiv = document.getElementById('config-loading');
    loadingDiv.style.display = 'block';
    loadingDiv.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div><span class="ms-2">Testing configuration...</span></div>';
    
    try {
        const response = await fetch(`${API_BASE}/config/test`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(newConfig)
        });
        
        const data = await response.json();
        
        if (data.feasible) {
            showToast(`Configuration is valid! Estimated cost: $${data.results.total_cost.toFixed(2)}`, 'success');
        } else {
            showToast('Configuration is infeasible - no valid solution found. Please adjust staff availability or shift requirements.', 'warning');
        }
        
    } catch (error) {
        showToast('Error testing configuration: ' + error.message, 'danger');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

async function resetConfig() {
    if (!confirm('Reset configuration to defaults? This will reload from config.json.')) {
        return;
    }
    showToast('Reloading configuration...', 'info');
    await loadConfig();
}

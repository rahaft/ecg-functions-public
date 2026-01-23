// Import Firebase modules
import { 
    onAuthStateChanged 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { 
    doc, 
    getDoc, 
    collection, 
    getDocs 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';
// Removed Firebase Storage - using Google Cloud Storage (GCS) URLs directly
import { 
    httpsCallable 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-functions.js';

// Global state
let recordData = null;
let leadsData = [];
let currentUser = null;

// Get record ID from URL
const urlParams = new URLSearchParams(window.location.search);
const recordId = urlParams.get('recordId');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (!recordId) {
        showError('No record ID provided');
        return;
    }

    setupAuth();
    initializeTabs();
});

function setupAuth() {
    onAuthStateChanged(window.auth, (user) => {
        currentUser = user;
        if (user) {
            loadRecordData();
        } else {
            showError('Please sign in to view records');
        }
    });
}

async function loadRecordData() {
    try {
        const loadingEl = document.getElementById('loading');
        loadingEl.textContent = 'Loading record data...';

        // Get record document
        const recordRef = doc(window.db, 'ecg_records', recordId);
        const recordDoc = await getDoc(recordRef);

        if (!recordDoc.exists()) {
            showError('Record not found');
            return;
        }

        recordData = { id: recordDoc.id, ...recordDoc.data() };

        // Check if user owns this record
        if (recordData.userId !== currentUser.uid) {
            showError('Access denied');
            return;
        }

        // Load time-series data
        const timeSeriesRef = collection(recordRef, 'timeseries');
        const timeSeriesSnapshot = await getDocs(timeSeriesRef);

        if (!timeSeriesSnapshot.empty) {
            // Use aggregated or first available
            const timeSeriesDoc = timeSeriesSnapshot.docs.find(d => d.id === 'aggregated') || timeSeriesSnapshot.docs[0];
            const tsData = timeSeriesDoc.data();
            leadsData = tsData.leads || [];
        } else {
            // Try loading from leads subcollection
            const leadsRef = collection(recordRef, 'leads');
            const leadsSnapshot = await getDocs(leadsRef);
            
            if (!leadsSnapshot.empty) {
                leadsData = leadsSnapshot.docs.map(doc => ({
                    name: doc.id,
                    values: doc.data().values || [],
                    sampling_rate: doc.data().samplingRate || 500,
                    duration: doc.data().duration || 0
                }));
            }
        }

        // Load first image if available
        if (recordData.imageUrls && recordData.imageUrls.length > 0) {
            const img = document.getElementById('original-image');
            img.src = recordData.imageUrls[0];
            img.style.display = 'block';
            document.getElementById('no-image').style.display = 'none';
        }

        // Display record info
        const recordInfo = document.getElementById('record-info');
        recordInfo.innerHTML = `
            <p><strong>Record ID:</strong> ${recordData.recordId || recordId}</p>
            <p><strong>Status:</strong> ${recordData.status || 'unknown'}</p>
            <p><strong>Images:</strong> ${recordData.imageCount || 0}</p>
            <p><strong>Created:</strong> ${recordData.createdAt ? new Date(recordData.createdAt.toDate()).toLocaleString() : 'Unknown'}</p>
        `;

        // Render data
        renderData();
        
        // Hide loading, show content
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';

    } catch (error) {
        console.error('Error loading record:', error);
        showError('Failed to load record: ' + error.message);
    }
}

function renderData() {
    // Update metrics
    const snr = recordData.snr || recordData.metadata?.quality?.mean_snr || 0;
    document.getElementById('snr-value').textContent = snr.toFixed(1);
    document.getElementById('leads-count').textContent = leadsData.length || 0;
    
    // Calculate duration from first lead
    const duration = leadsData.length > 0 ? (leadsData[0].duration || leadsData[0].values.length / (leadsData[0].sampling_rate || 500)) : 0;
    document.getElementById('duration-value').textContent = duration.toFixed(1);

    // Update status badge
    const statusBadge = document.getElementById('status-badge');
    statusBadge.textContent = recordData.status || 'unknown';
    statusBadge.className = `status-badge status-${recordData.status || 'unknown'}`;

    // Render ECG leads
    if (leadsData.length > 0) {
        renderECGLeads(leadsData);
        renderComparisonChart(leadsData[0] || leadsData[1]); // Use first or second lead
    } else {
        document.getElementById('ecg-leads-grid').innerHTML = '<p class="empty-state">No signal data available. Processing may still be in progress.</p>';
    }
}

function renderECGLeads(leads) {
    const grid = document.getElementById('ecg-leads-grid');
    grid.innerHTML = '';
    
    leads.forEach(lead => {
        const card = document.createElement('div');
        card.className = 'lead-card';
        
        const title = document.createElement('h4');
        title.textContent = `Lead ${lead.name}`;
        
        const chartContainer = document.createElement('div');
        chartContainer.className = 'chart-container';
        
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        
        card.appendChild(title);
        card.appendChild(chartContainer);
        grid.appendChild(card);
        
        // Create chart
        createLeadChart(canvas, lead);
    });
}

function createLeadChart(canvas, lead) {
    const ctx = canvas.getContext('2d');
    
    // Downsample for display
    const displayData = downsample(lead.values || [], 500);
    const samplingRate = lead.sampling_rate || 500;
    const labels = displayData.map((_, i) => (i / samplingRate * (lead.values.length / displayData.length)).toFixed(2));
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: displayData,
                borderColor: '#2563eb',
                borderWidth: 1.5,
                tension: 0.1,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Time (s)' },
                    ticks: { maxTicksLimit: 5 }
                },
                y: {
                    display: true,
                    title: { display: true, text: 'mV' }
                }
            },
            animation: { duration: 0 }
        }
    });
}

function renderComparisonChart(lead) {
    if (!lead || !lead.values) return;
    
    const ctx = document.getElementById('comparison-chart').getContext('2d');
    
    const displayData = downsample(lead.values, 1000);
    const samplingRate = lead.sampling_rate || 500;
    const labels = displayData.map((_, i) => (i / samplingRate * (lead.values.length / displayData.length)).toFixed(2));
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Extracted Signal',
                    data: displayData,
                    borderColor: '#2563eb',
                    borderWidth: 2,
                    tension: 0.1,
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Time (seconds)' }
                },
                y: {
                    title: { display: true, text: 'Amplitude (mV)' }
                }
            }
        }
    });
}

function downsample(data, targetLength) {
    if (!data || data.length === 0) return [];
    if (data.length <= targetLength) return data;
    const step = data.length / targetLength;
    const result = [];
    for (let i = 0; i < targetLength; i++) {
        result.push(data[Math.floor(i * step)]);
    }
    return result;
}

function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    const errorEl = document.getElementById('error');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function downloadJSON() {
    const data = {
        recordId: recordData.recordId || recordId,
        status: recordData.status,
        snr: recordData.snr,
        leads: leadsData,
        metadata: recordData.metadata || {}
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ecg_${recordId}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

function downloadCSV() {
    let csv = 'lead,time,value\n';
    leadsData.forEach(lead => {
        const samplingRate = lead.sampling_rate || 500;
        (lead.values || []).forEach((value, index) => {
            const time = (index / samplingRate).toFixed(4);
            csv += `${lead.name},${time},${value.toFixed(6)}\n`;
        });
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ecg_${recordId}.csv`;
    link.click();
    URL.revokeObjectURL(url);
}

async function downloadSubmission() {
    try {
        const generateSubmissionFunction = httpsCallable(window.functions, 'generateSubmission');
        const result = await generateSubmissionFunction({ recordId: recordId });
        
        if (result.data.success) {
            // Open download URL
            window.open(result.data.downloadUrl, '_blank');
        } else {
            alert('Failed to generate submission: ' + (result.data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error generating submission:', error);
        alert('Failed to generate submission: ' + error.message);
    }
}

// Import Firebase modules
import { 
    signInAnonymously, 
    signInWithPopup,
    GoogleAuthProvider,
    onAuthStateChanged, 
    signOut 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { 
    ref, 
    uploadBytesResumable, 
    getDownloadURL 
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js';
import { 
    collection, 
    addDoc, 
    query, 
    where, 
    getDocs, 
    orderBy, 
    doc, 
    updateDoc,
    getDoc,
    serverTimestamp,
    onSnapshot
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';
import { httpsCallable } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-functions.js';

// Global state
let selectedFiles = [];
let bulkFiles = []; // For bulk upload
let currentUser = null;

// DOM elements
const signInBtn = document.getElementById('sign-in-btn');
const signOutBtn = document.getElementById('sign-out-btn');
const authStatus = document.getElementById('auth-status');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const recordIdInput = document.getElementById('record-id');
const uploadBtn = document.getElementById('upload-btn');
const clearBtn = document.getElementById('clear-btn');
const fileList = document.getElementById('file-list');
const uploadProgress = document.getElementById('upload-progress');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const recordsList = document.getElementById('records-list');

// Bulk upload elements
const bulkUploadArea = document.getElementById('bulk-upload-area');
const bulkFileInput = document.getElementById('bulk-file-input');
const selectFolderBtn = document.getElementById('select-folder-btn');
const bulkFileList = document.getElementById('bulk-file-list');
const bulkUploadBtn = document.getElementById('bulk-upload-btn');
const bulkClearBtn = document.getElementById('bulk-clear-btn');
const bulkUploadProgress = document.getElementById('bulk-upload-progress');
const bulkProgressFill = document.getElementById('bulk-progress-fill');
const bulkProgressText = document.getElementById('bulk-progress-text');
const bulkStats = document.getElementById('bulk-stats');
const autoRecordIdCheckbox = document.getElementById('auto-record-id');
const manualRecordIdGroup = document.getElementById('manual-record-id-group');
const bulkRecordIdInput = document.getElementById('bulk-record-id');

// Modal elements
const signInModal = document.getElementById('sign-in-modal');
const closeModalBtn = document.getElementById('close-modal');
const googleSignInBtn = document.getElementById('google-sign-in-btn');
const anonymousSignInBtn = document.getElementById('anonymous-sign-in-btn');

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Verify Firebase is initialized
    if (!window.auth) {
        console.error('Firebase Auth not initialized!');
        alert('Firebase configuration error. Please refresh the page.');
        return;
    }
    
    console.log('Firebase initialized:', {
        auth: !!window.auth,
        storage: !!window.storage,
        db: !!window.db,
        functions: !!window.functions
    });
    
    setupAuth();
    setupUpload();
    setupBulkUpload();
    setupRecords();
});

// Authentication
function setupAuth() {
    // Show sign-in modal when sign-in button is clicked
    signInBtn.addEventListener('click', () => {
        signInModal.style.display = 'flex';
    });

    // Close modal handlers
    closeModalBtn.addEventListener('click', () => {
        signInModal.style.display = 'none';
    });

    signInModal.addEventListener('click', (e) => {
        if (e.target === signInModal) {
            signInModal.style.display = 'none';
        }
    });

    // Google Sign-in
    googleSignInBtn.addEventListener('click', async () => {
        try {
            console.log('Attempting Google sign in...');
            await signInWithPopup(window.auth, googleProvider);
            console.log('Google sign in successful!');
            signInModal.style.display = 'none';
        } catch (error) {
            console.error('Google sign in error:', error);
            let errorMessage = 'Failed to sign in with Google. ';
            
            if (error.code === 'auth/popup-closed-by-user') {
                errorMessage = 'Sign-in popup was closed. Please try again.';
            } else if (error.code === 'auth/popup-blocked') {
                errorMessage = 'Sign-in popup was blocked. Please allow popups for this site.';
            } else {
                errorMessage += error.message || error.code || 'Unknown error';
            }
            
            alert(errorMessage);
        }
    });

    // Anonymous Sign-in
    anonymousSignInBtn.addEventListener('click', async () => {
        try {
            console.log('Attempting anonymous sign in...');
            await signInAnonymously(window.auth);
            console.log('Anonymous sign in successful!');
            signInModal.style.display = 'none';
        } catch (error) {
            console.error('Anonymous sign in error:', error);
            let errorMessage = 'Failed to sign in. ';
            
            if (error.code === 'auth/operation-not-allowed') {
                errorMessage += 'Anonymous authentication is not enabled in Firebase Console. Please enable it in Authentication > Sign-in method.';
            } else if (error.code === 'auth/admin-restricted-operation') {
                errorMessage += 'API key restrictions are blocking authentication. Please check API key settings in Google Cloud Console.';
            } else {
                errorMessage += error.message || error.code || 'Unknown error';
            }
            
            alert(errorMessage);
        }
    });

    signOutBtn.addEventListener('click', async () => {
        try {
            await signOut(window.auth);
        } catch (error) {
            console.error('Sign out error:', error);
        }
    });

    onAuthStateChanged(window.auth, (user) => {
        currentUser = user;
        if (user) {
            // Display user info - show email if available, otherwise show UID
            const displayName = user.email || user.displayName || `User ${user.uid.substring(0, 8)}...`;
            authStatus.textContent = `Signed in as: ${displayName}`;
            if (user.photoURL) {
                authStatus.innerHTML = `<img src="${user.photoURL}" alt="User" style="width: 20px; height: 20px; border-radius: 50%; margin-right: 8px; vertical-align: middle;">${displayName}`;
            }
            signInBtn.style.display = 'none';
            signOutBtn.style.display = 'block';
            signInModal.style.display = 'none';
            uploadArea.style.pointerEvents = 'auto';
            uploadArea.style.opacity = '1';
        } else {
            authStatus.textContent = 'Not signed in';
            signInBtn.style.display = 'block';
            signOutBtn.style.display = 'none';
            uploadArea.style.pointerEvents = 'none';
            uploadArea.style.opacity = '0.5';
        }
    });
}

// Upload functionality
function setupUpload() {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        if (currentUser) {
            fileInput.click();
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (currentUser && e.dataTransfer.files.length > 0) {
            handleFiles(Array.from(e.dataTransfer.files));
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFiles(Array.from(e.target.files));
        }
    });

    // Upload button
    uploadBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0 || !recordIdInput.value.trim()) {
            alert('Please select files and enter a record ID');
            return;
        }
        await uploadFiles();
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
        clearFiles();
    });

    // Record ID validation
    recordIdInput.addEventListener('input', () => {
        updateUploadButtonState();
    });
}

// Add event listener for bulk record ID input
if (bulkRecordIdInput) {
    bulkRecordIdInput.addEventListener('input', () => {
        updateBulkUploadButtonState();
    });
}

function handleFiles(files) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        alert('Please select image files only');
        return;
    }

    // Add new files to selection
    imageFiles.forEach(file => {
        if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });

    renderFileList();
    updateUploadButtonState();
}

function renderFileList() {
    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
        return;
    }

    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})" title="Remove file">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `).join('');
}

window.removeFile = (index) => {
    selectedFiles.splice(index, 1);
    renderFileList();
    updateUploadButtonState();
};

function updateUploadButtonState() {
    uploadBtn.disabled = selectedFiles.length === 0 || !recordIdInput.value.trim();
}

function clearFiles() {
    selectedFiles = [];
    recordIdInput.value = '';
    fileInput.value = '';
    renderFileList();
    updateUploadButtonState();
    uploadProgress.style.display = 'none';
}

async function uploadFiles() {
    if (!currentUser) {
        alert('Please sign in first');
        return;
    }

    const recordId = recordIdInput.value.trim();
    if (!recordId) {
        alert('Please enter a record ID');
        return;
    }

    uploadBtn.disabled = true;
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Preparing upload...';

    try {
        // Create record in Firestore
        const recordRef = await addDoc(collection(window.db, 'ecg_records'), {
            userId: currentUser.uid,
            recordId: recordId,
            status: 'uploading',
            imageCount: selectedFiles.length,
            createdAt: serverTimestamp(),
            updatedAt: serverTimestamp()
        });

        const recordId_doc = recordRef.id;

        // Upload files
        const uploadPromises = selectedFiles.map((file, index) => 
            uploadFile(file, currentUser.uid, recordId_doc, index)
        );

        let completed = 0;
        const total = selectedFiles.length;

        // Track progress
        uploadPromises.forEach(promise => {
            promise.then(() => {
                completed++;
                const progress = (completed / total) * 100;
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `Uploading ${completed}/${total} files...`;
            });
        });

        // Wait for all uploads
        const imageUrls = await Promise.all(uploadPromises);

        // Update record with image URLs and status
        await updateDoc(recordRef, {
            status: 'uploaded',
            imageUrls: imageUrls,
            updatedAt: serverTimestamp()
        });

        // Add image metadata to subcollection
        for (let i = 0; i < selectedFiles.length; i++) {
            await addDoc(collection(window.db, `ecg_records/${recordId_doc}/images`), {
                fileName: selectedFiles[i].name,
                fileSize: selectedFiles[i].size,
                fileType: selectedFiles[i].type,
                storagePath: `ecg_images/${currentUser.uid}/${recordId_doc}/${selectedFiles[i].name}`,
                downloadUrl: imageUrls[i],
                uploadedAt: serverTimestamp()
            });
        }

        progressText.textContent = 'Upload complete!';
        setTimeout(() => {
            uploadProgress.style.display = 'none';
            clearFiles();
        }, 2000);

        // Refresh records list
        loadRecords();

    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed: ' + error.message);
        progressText.textContent = 'Upload failed';
        uploadBtn.disabled = false;
    }
}

function uploadFile(file, userId, recordId, index) {
    return new Promise((resolve, reject) => {
        const storagePath = `ecg_images/${userId}/${recordId}/${file.name}`;
        const storageRef = ref(window.storage, storagePath);
        const uploadTask = uploadBytesResumable(storageRef, file);

        uploadTask.on(
            'state_changed',
            (snapshot) => {
                // Individual file progress could be tracked here
            },
            (error) => {
                reject(error);
            },
            async () => {
                try {
                    const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
                    resolve(downloadURL);
                } catch (error) {
                    reject(error);
                }
            }
        );
    });
}

// Bulk Upload functionality
function setupBulkUpload() {
    // Folder selection
    selectFolderBtn.addEventListener('click', () => {
        bulkFileInput.click();
    });

    bulkFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleBulkFiles(Array.from(e.target.files));
        }
    });

    // Auto-detect record ID toggle
    autoRecordIdCheckbox.addEventListener('change', (e) => {
        manualRecordIdGroup.style.display = e.target.checked ? 'none' : 'block';
        updateBulkUploadButtonState();
    });

    // Bulk upload button
    bulkUploadBtn.addEventListener('click', async () => {
        await uploadBulkFiles();
    });

    // Clear button
    bulkClearBtn.addEventListener('click', () => {
        clearBulkFiles();
    });
}

function handleBulkFiles(files) {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
        alert('Please select image files only');
        return;
    }

    bulkFiles = imageFiles;
    renderBulkFileList();
    updateBulkUploadButtonState();
}

function renderBulkFileList() {
    if (bulkFiles.length === 0) {
        bulkFileList.innerHTML = '';
        return;
    }

    // Group files by record ID if auto-detect is enabled
    let groupedFiles = {};
    if (autoRecordIdCheckbox.checked) {
        bulkFiles.forEach(file => {
            // Extract record ID from file path (folder name or filename pattern)
            const recordId = extractRecordIdFromPath(file.webkitRelativePath || file.name);
            if (!groupedFiles[recordId]) {
                groupedFiles[recordId] = [];
            }
            groupedFiles[recordId].push(file);
        });
    } else {
        // All files in one group
        groupedFiles['all'] = bulkFiles;
    }

    const totalSize = bulkFiles.reduce((sum, file) => sum + file.size, 0);
    const recordCount = Object.keys(groupedFiles).length;

    bulkFileList.innerHTML = `
        <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
            <strong>Summary:</strong> ${bulkFiles.length} files, ${formatFileSize(totalSize)}, ${recordCount} record(s)
        </div>
        <div style="max-height: 300px; overflow-y: auto;">
            ${Object.entries(groupedFiles).map(([recordId, files]) => `
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <strong>Record ID: ${recordId}</strong> (${files.length} files)
                    <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                        ${files.slice(0, 5).map(f => f.name).join(', ')}${files.length > 5 ? ` ... and ${files.length - 5} more` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function extractRecordIdFromPath(filePath) {
    // Try to extract record ID from path
    // Examples:
    // - "train/record_001/image1.png" -> "record_001"
    // - "record_001/image1.png" -> "record_001"
    // - "record_001.png" -> "record_001"
    
    const parts = filePath.split('/');
    
    // If it's in a folder, use folder name
    if (parts.length > 1) {
        const folderName = parts[parts.length - 2];
        // Remove common prefixes/suffixes
        return folderName.replace(/^(train|test|val)_?/i, '').replace(/_?$/, '');
    }
    
    // Otherwise, try to extract from filename
    const fileName = parts[parts.length - 1];
    // Match patterns like "record_001", "ECG_001", "001", etc.
    const match = fileName.match(/(?:record|ecg|id)[_-]?(\d+)|^(\d+)/i);
    if (match) {
        return match[1] || match[2] || 'unknown';
    }
    
    // Fallback: use filename without extension
    return fileName.replace(/\.[^/.]+$/, '');
}

function updateBulkUploadButtonState() {
    const hasFiles = bulkFiles.length > 0;
    const hasRecordId = autoRecordIdCheckbox.checked || bulkRecordIdInput.value.trim();
    bulkUploadBtn.disabled = !hasFiles || !hasRecordId;
}

function clearBulkFiles() {
    bulkFiles = [];
    bulkFileInput.value = '';
    bulkRecordIdInput.value = '';
    renderBulkFileList();
    updateBulkUploadButtonState();
    bulkUploadProgress.style.display = 'none';
}

async function uploadBulkFiles() {
    if (!currentUser) {
        alert('Please sign in first');
        return;
    }

    if (bulkFiles.length === 0) {
        alert('Please select files to upload');
        return;
    }

    bulkUploadBtn.disabled = true;
    bulkUploadProgress.style.display = 'block';
    bulkProgressFill.style.width = '0%';
    bulkProgressText.textContent = 'Preparing bulk upload...';
    bulkStats.textContent = '';

    try {
        // Group files by record ID
        let groupedFiles = {};
        
        if (autoRecordIdCheckbox.checked) {
            bulkFiles.forEach(file => {
                const recordId = extractRecordIdFromPath(file.webkitRelativePath || file.name);
                if (!groupedFiles[recordId]) {
                    groupedFiles[recordId] = [];
                }
                groupedFiles[recordId].push(file);
            });
        } else {
            const recordId = bulkRecordIdInput.value.trim() || 'BULK_UPLOAD';
            groupedFiles[recordId] = bulkFiles;
        }

        const recordIds = Object.keys(groupedFiles);
        let totalUploaded = 0;
        let totalRecords = recordIds.length;
        let completedRecords = 0;
        let errors = [];

        // Upload each record group
        for (const recordId of recordIds) {
            const files = groupedFiles[recordId];
            
            bulkProgressText.textContent = `Uploading record ${completedRecords + 1}/${totalRecords}: ${recordId}`;
            bulkStats.textContent = `Total files uploaded: ${totalUploaded}/${bulkFiles.length}`;

            try {
                // Create record in Firestore
                const recordRef = await addDoc(collection(window.db, 'ecg_records'), {
                    userId: currentUser.uid,
                    recordId: recordId,
                    status: 'uploading',
                    imageCount: files.length,
                    createdAt: serverTimestamp(),
                    updatedAt: serverTimestamp(),
                    bulkUpload: true
                });

                const recordId_doc = recordRef.id;

                // Upload files for this record
                const uploadPromises = files.map((file, index) => 
                    uploadFile(file, currentUser.uid, recordId_doc, index)
                );

                let completed = 0;
                const total = files.length;

                // Track progress
                uploadPromises.forEach(promise => {
                    promise.then(() => {
                        completed++;
                        totalUploaded++;
                        const overallProgress = (totalUploaded / bulkFiles.length) * 100;
                        bulkProgressFill.style.width = `${overallProgress}%`;
                        bulkStats.textContent = `Record ${completedRecords + 1}/${totalRecords}: ${completed}/${total} files | Total: ${totalUploaded}/${bulkFiles.length}`;
                    }).catch(err => {
                        errors.push(`Error uploading ${file.name}: ${err.message}`);
                    });
                });

                // Wait for all uploads for this record
                const imageUrls = await Promise.all(uploadPromises);

                // Update record with image URLs and status
                await updateDoc(recordRef, {
                    status: 'uploaded',
                    imageUrls: imageUrls,
                    updatedAt: serverTimestamp()
                });

                // Add image metadata to subcollection
                for (let i = 0; i < files.length; i++) {
                    await addDoc(collection(window.db, `ecg_records/${recordId_doc}/images`), {
                        fileName: files[i].name,
                        fileSize: files[i].size,
                        fileType: files[i].type,
                        storagePath: `ecg_images/${currentUser.uid}/${recordId_doc}/${files[i].name}`,
                        downloadUrl: imageUrls[i],
                        uploadedAt: serverTimestamp()
                    });
                }

                completedRecords++;
            } catch (error) {
                console.error(`Error uploading record ${recordId}:`, error);
                errors.push(`Error uploading record ${recordId}: ${error.message}`);
            }
        }

        bulkProgressText.textContent = 'Bulk upload complete!';
        bulkStats.textContent = `Successfully uploaded ${completedRecords}/${totalRecords} records (${totalUploaded} files)${errors.length > 0 ? ` | ${errors.length} errors` : ''}`;
        
        if (errors.length > 0) {
            console.error('Upload errors:', errors);
        }

        setTimeout(() => {
            bulkUploadProgress.style.display = 'none';
            clearBulkFiles();
        }, 3000);

        // Refresh records list
        loadRecords();

    } catch (error) {
        console.error('Bulk upload error:', error);
        alert('Bulk upload failed: ' + error.message);
        bulkProgressText.textContent = 'Bulk upload failed';
        bulkUploadBtn.disabled = false;
    }
}

// Records management
function setupRecords() {
    if (currentUser) {
        loadRecords();
    }

    onAuthStateChanged(window.auth, (user) => {
        if (user) {
            loadRecords();
            
            // Real-time updates
            const q = query(
                collection(window.db, 'ecg_records'),
                where('userId', '==', user.uid),
                orderBy('createdAt', 'desc')
            );

            onSnapshot(q, (snapshot) => {
                loadRecords();
            });
        } else {
            recordsList.innerHTML = '<p class="empty-state">Please sign in to view your records.</p>';
        }
    });
}

async function loadRecords() {
    if (!currentUser) {
        return;
    }

    try {
        const q = query(
            collection(window.db, 'ecg_records'),
            where('userId', '==', currentUser.uid),
            orderBy('createdAt', 'desc')
        );

        const querySnapshot = await getDocs(q);
        
        if (querySnapshot.empty) {
            recordsList.innerHTML = '<p class="empty-state">No ECG records yet. Upload images to get started.</p>';
            return;
        }

        recordsList.innerHTML = querySnapshot.docs.map(doc => {
            const data = doc.data();
            return createRecordCard(doc.id, data);
        }).join('');

    } catch (error) {
        console.error('Error loading records:', error);
        recordsList.innerHTML = '<p class="empty-state">Error loading records. Please try again.</p>';
    }
}

function createRecordCard(docId, data) {
    const statusClass = `status-${data.status || 'uploaded'}`;
    const createdAt = data.createdAt ? new Date(data.createdAt.toDate()).toLocaleString() : 'Unknown';
    
    return `
        <div class="record-card">
            <div class="record-header">
                <div class="record-id">${data.recordId || 'Unknown'}</div>
                <span class="record-status ${statusClass}">${data.status || 'uploaded'}</span>
            </div>
            <div class="record-meta">
                <div><strong>Images:</strong> ${data.imageCount || 0}</div>
                <div><strong>Created:</strong> ${createdAt}</div>
            </div>
            <div class="record-actions">
                <button class="btn btn-primary btn-small" onclick="viewRecord('${docId}')">View Details</button>
                <button class="btn btn-secondary btn-small" onclick="processRecord('${docId}')">Process</button>
            </div>
        </div>
    `;
}

window.viewRecord = (docId) => {
    // Navigate to visualization page
    window.location.href = `visualization.html?recordId=${docId}`;
};

window.processRecord = async (docId) => {
    if (!currentUser) {
        alert('Please sign in first');
        return;
    }

    try {
        const processRecordFunction = httpsCallable(window.functions, 'processRecord');
        const result = await processRecordFunction({ recordId: docId });
        
        if (result.data.success) {
            alert('Processing started! The record will be processed automatically.');
            // Refresh records list
            loadRecords();
        } else {
            alert('Processing failed: ' + (result.data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error starting processing:', error);
        alert('Failed to start processing: ' + error.message);
    }
};

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

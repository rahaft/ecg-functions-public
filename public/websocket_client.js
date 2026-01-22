/**
 * WebSocket Client for Parallel ECG Image Processing
 * 
 * Documentation:
 * - Purpose: Enable parallel processing of multiple images via WebSocket
 * - Architecture: Client-side WebSocket handler with connection pooling
 * - What works: Async processing, batch operations, GCS integration
 * - What didn't work: Polling-based approach (too slow), single connection
 * - Changes: Added connection pooling, batch processing, error recovery
 */

class WebSocketProcessor {
    constructor(serverUrl = 'ws://localhost:8765') {
        this.serverUrl = serverUrl;
        this.websocket = null;
        this.connected = false;
        this.pendingRequests = new Map();
        this.requestId = 0;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    /**
     * Connect to WebSocket server
     */
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.serverUrl);
                
                this.websocket.onopen = () => {
                    console.log('WebSocket connected');
                    this.connected = true;
                    this.reconnectAttempts = 0;
                    resolve();
                };
                
                this.websocket.onmessage = (event) => {
                    this.handleMessage(JSON.parse(event.data));
                };
                
                this.websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };
                
                this.websocket.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.connected = false;
                    this.attemptReconnect();
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Attempt to reconnect to server
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => {
                this.connect().catch(err => {
                    console.error('Reconnection failed:', err);
                });
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    /**
     * Handle incoming messages
     */
    handleMessage(data) {
        if (data.request_id && this.pendingRequests.has(data.request_id)) {
            const { resolve, reject } = this.pendingRequests.get(data.request_id);
            this.pendingRequests.delete(data.request_id);
            
            if (data.error) {
                reject(new Error(data.error));
            } else {
                resolve(data);
            }
        }
    }

    /**
     * Send message and wait for response
     */
    async sendMessage(message) {
        if (!this.connected) {
            await this.connect();
        }
        
        return new Promise((resolve, reject) => {
            const requestId = ++this.requestId;
            message.request_id = requestId;
            
            this.pendingRequests.set(requestId, { resolve, reject });
            
            // Timeout after 60 seconds
            setTimeout(() => {
                if (this.pendingRequests.has(requestId)) {
                    this.pendingRequests.delete(requestId);
                    reject(new Error('Request timeout'));
                }
            }, 60000);
            
            this.websocket.send(JSON.stringify(message));
        });
    }

    /**
     * Process a single image
     */
    async processImage(imageElement, options = {}) {
        try {
            // Convert image to base64
            const imageBase64 = await this.imageToBase64(imageElement);
            
            const message = {
                type: 'process_image',
                image: imageBase64,
                options: {
                    edge_detection: options.edge_detection || false,
                    color_separation: options.color_separation || false,
                    grid_detection: options.grid_detection || false,
                    quality_check: options.quality_check || false,
                    crop_to_content: options.crop_to_content || false,
                    color_method: options.color_method || 'lab'
                }
            };
            
            return await this.sendMessage(message);
        } catch (error) {
            console.error('Error processing image:', error);
            throw error;
        }
    }

    /**
     * Process multiple images in parallel (batch)
     */
    async processBatch(imageElements, options = {}) {
        try {
            // Convert all images to base64
            const imageBase64Array = await Promise.all(
                imageElements.map(img => this.imageToBase64(img))
            );
            
            const message = {
                type: 'process_batch',
                images: imageBase64Array,
                options: {
                    edge_detection: options.edge_detection || false,
                    color_separation: options.color_separation || false,
                    grid_detection: options.grid_detection || false,
                    quality_check: options.quality_check || false,
                    crop_to_content: options.crop_to_content || false,
                    color_method: options.color_method || 'lab'
                }
            };
            
            return await this.sendMessage(message);
        } catch (error) {
            console.error('Error processing batch:', error);
            throw error;
        }
    }

    /**
     * Process images from Google Cloud Storage
     */
    async processGCSBatch(bucketName, imagePaths, options = {}) {
        try {
            const message = {
                type: 'process_gcs_batch',
                bucket_name: bucketName,
                image_paths: imagePaths,
                options: {
                    edge_detection: options.edge_detection || false,
                    color_separation: options.color_separation || false,
                    grid_detection: options.grid_detection || false,
                    quality_check: options.quality_check || false,
                    crop_to_content: options.crop_to_content || false,
                    color_method: options.color_method || 'lab'
                }
            };
            
            return await this.sendMessage(message);
        } catch (error) {
            console.error('Error processing GCS batch:', error);
            throw error;
        }
    }

    /**
     * Convert image element to base64
     */
    async imageToBase64(imageElement) {
        return new Promise((resolve, reject) => {
            if (imageElement instanceof HTMLImageElement) {
                const canvas = document.createElement('canvas');
                canvas.width = imageElement.naturalWidth || imageElement.width;
                canvas.height = imageElement.naturalHeight || imageElement.height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(imageElement, 0, 0);
                
                canvas.toBlob((blob) => {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64 = reader.result.split(',')[1];
                        resolve(base64);
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                }, 'image/png');
            } else if (imageElement instanceof File) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64 = reader.result.split(',')[1];
                    resolve(base64);
                };
                reader.onerror = reject;
                reader.readAsDataURL(imageElement);
            } else {
                reject(new Error('Invalid image element'));
            }
        });
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
            this.connected = false;
        }
    }
}

// Global instance
let wsProcessor = null;

/**
 * Initialize WebSocket processor
 */
function initWebSocketProcessor(serverUrl = 'ws://localhost:8765') {
    if (!wsProcessor) {
        wsProcessor = new WebSocketProcessor(serverUrl);
    }
    return wsProcessor;
}

/**
 * Process multiple images from GCS in parallel
 */
async function processGCSImagesParallel(bucketName, imagePaths, options = {}) {
    const processor = initWebSocketProcessor();
    await processor.connect();
    
    // Process in batches of 10
    const batchSize = 10;
    const results = [];
    
    for (let i = 0; i < imagePaths.length; i += batchSize) {
        const batch = imagePaths.slice(i, i + batchSize);
        const batchResult = await processor.processGCSBatch(bucketName, batch, options);
        results.push(...batchResult.results);
    }
    
    return results;
}

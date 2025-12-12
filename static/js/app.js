document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const switchCameraBtn = document.getElementById('switch-camera-btn');
    const resultsPanel = document.getElementById('results-panel');
    const closeResultsBtn = document.getElementById('close-results');
    const loader = document.getElementById('loader');
    const analysisContent = document.getElementById('analysis-content');

    let currentStream = null;
    let facingMode = 'environment'; // Default to rear camera

    // Initialize Camera
    async function startCamera() {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }

        try {
            const constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            };
            
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = stream;
            currentStream = stream;
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Could not access camera. Please ensure you have given permission.");
        }
    }

    // Switch Camera
    switchCameraBtn.addEventListener('click', () => {
        facingMode = facingMode === 'environment' ? 'user' : 'environment';
        startCamera();
    });

    // Capture and Scan
    captureBtn.addEventListener('click', async () => {
        // Draw video frame to canvas
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to blob
        canvas.toBlob(async (blob) => {
            if (!blob) return;

            // Show loading state
            resultsPanel.style.display = 'block';
            loader.style.display = 'flex';
            analysisContent.innerHTML = '';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('file', blob, 'scan.jpg');

            try {
                const response = await fetch('/scan', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Scan failed');

                const data = await response.json();
                displayResults(data);

            } catch (err) {
                console.error(err);
                analysisContent.innerHTML = `<div class="result-card" style="border-left: 4px solid var(--danger-color)">
                    <p>Error processing image. Please try again.</p>
                </div>`;
            } finally {
                loader.style.display = 'none';
            }
        }, 'image/jpeg', 0.9);
    });

    // Display Results
    function displayResults(data) {
        const html = `
            <div class="result-card">
                <div class="result-item">
                    <span class="label">Product</span>
                    <span class="value">${data.product_name}</span>
                </div>
                <div class="result-item">
                    <span class="label">Status</span>
                    <span class="status-badge ${data.compliance_status === 'Compliant' ? 'status-pass' : 'status-fail'}">
                        ${data.compliance_status}
                    </span>
                </div>
            </div>

            <div class="result-card">
                <h3 style="font-size: 0.9rem; margin-bottom: 10px; color: var(--accent-color);">Details</h3>
                ${Object.entries(data.details).map(([key, value]) => `
                    <div class="result-item">
                        <span class="label" style="text-transform: capitalize">${key.replace('_', ' ')}</span>
                        <span class="value">${value}</span>
                    </div>
                `).join('')}
            </div>
            
            <div style="font-size: 0.8rem; color: var(--secondary-color); text-align: center; margin-top: 10px;">
                ${data.message}
            </div>
        `;
        analysisContent.innerHTML = html;
    }

    // Close Results
    closeResultsBtn.addEventListener('click', () => {
        resultsPanel.style.display = 'none';
    });

    // Start camera on load
    startCamera();
});

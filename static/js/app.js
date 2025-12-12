document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('capture-btn');
    const switchCameraBtn = document.getElementById('switch-camera-btn');
    const resultsPanel = document.getElementById('results-panel');
    const closeResultsBtn = document.getElementById('close-results');
    const loader = document.getElementById('loader');
    const analysisContent = document.getElementById('analysis-content');

    // Note: We are now using Server-Side Camera (Pi Camera)
    // So we don't need getUserMedia for the main functionality.
    // However, if we want a "Viewfinder", we would need MJPEG stream.
    // For now, we will just show a static placeholder or "Ready to Scan" message in the video area.

    // Optional: Try to start camera just in case user is on a phone/laptop testing it, 
    // but the actual scan will trigger the Pi Camera.
    // If running on Pi with no display, this might fail, which is fine.
    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            console.log("Client-side camera not available (expected if running on Pi headless)");
            // Show a placeholder
            video.style.display = 'none';
            const container = document.querySelector('.camera-container');
            const msg = document.createElement('div');
            msg.innerHTML = '<div style="color:white; text-align:center; padding-top:40%;"><i class="fa-solid fa-camera fa-3x"></i><br><br>Pi Camera Ready</div>';
            msg.style.position = 'absolute';
            msg.style.top = '0';
            msg.style.width = '100%';
            msg.style.height = '100%';
            container.appendChild(msg);
        }
    }
    startCamera();

    // Capture and Scan (Server-Side)
    captureBtn.addEventListener('click', async () => {
        // Show loading state
        resultsPanel.style.display = 'block';
        loader.style.display = 'flex';
        analysisContent.innerHTML = '';

        try {
            // Trigger Server-Side Capture
            const response = await fetch('/scan', {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Scan failed');

            const data = await response.json();

            // Show the captured image
            if (data.image_url) {
                let imgPreview = document.getElementById('captured-preview');
                if (!imgPreview) {
                    imgPreview = document.createElement('img');
                    imgPreview.id = 'captured-preview';
                    imgPreview.style.width = '100%';
                    imgPreview.style.borderRadius = '12px';
                    imgPreview.style.marginBottom = '20px';
                    // Insert before analysis content
                    analysisContent.parentNode.insertBefore(imgPreview, analysisContent);
                }
                imgPreview.src = data.image_url + '?t=' + new Date().getTime(); // Prevent caching
                imgPreview.style.display = 'block';
            }

            displayResults(data);

        } catch (err) {
            console.error(err);
            analysisContent.innerHTML = `<div class="result-card" style="border-left: 4px solid var(--danger-color)">
                <p>Error processing image. Please try again.</p>
                <p style="font-size:0.8rem; color: #aaa;">${err.message}</p>
            </div>`;
        } finally {
            loader.style.display = 'none';
        }
    });

    // Display Results
    function displayResults(data) {
        const details = data.details;

        // Generate Checklist HTML
        const checklistHtml = Object.entries(details).map(([key, item]) => `
            <div class="result-item" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <i class="fa-solid ${item.found ? 'fa-circle-check' : 'fa-circle-xmark'}" 
                       style="color: ${item.found ? 'var(--success-color)' : 'var(--danger-color)'}"></i>
                    <span class="label" style="color: #fff;">${item.label}</span>
                </div>
                <div style="margin-left: 26px; font-size: 0.8rem; color: var(--secondary-color);">
                    ${item.value}
                </div>
            </div>
        `).join('');

        const html = `
            <div class="result-card" style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: ${data.compliance_score === 100 ? 'var(--success-color)' : (data.compliance_score >= 70 ? 'var(--warning-color)' : 'var(--danger-color)')}">
                    ${data.compliance_score}%
                </div>
                <div style="font-size: 0.9rem; color: var(--secondary-color); margin-bottom: 10px;">Compliance Score</div>
                <span class="status-badge ${data.compliance_status === 'Fully Compliant' ? 'status-pass' : 'status-fail'}" 
                      style="background: ${data.compliance_status === 'Partially Compliant' ? 'rgba(245, 158, 11, 0.2)' : ''}; 
                             color: ${data.compliance_status === 'Partially Compliant' ? 'var(--warning-color)' : ''}">
                    ${data.compliance_status}
                </span>
            </div>

            <div class="result-card">
                <h3 style="font-size: 0.9rem; margin-bottom: 15px; color: var(--accent-color); border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <i class="fa-solid fa-list-check"></i> Metrology Act Checklist
                </h3>
                ${checklistHtml}
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
        // Hide preview image when closing
        const imgPreview = document.getElementById('captured-preview');
        if (imgPreview) imgPreview.style.display = 'none';
    });
});

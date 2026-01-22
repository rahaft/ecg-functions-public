/**
 * Footer Copy Functionality
 * Makes version footer clickable to copy version info
 */

(function() {
    'use strict';
    
    function initFooterCopy() {
        // Find version footer elements
        const versionEl = document.getElementById('app-version');
        const buildEl = document.getElementById('app-build-timestamp');
        const dateEl = document.getElementById('app-build-date');
        const sdkEl = document.getElementById('app-firebase-sdk');
        
        // Find container (could be .version-info or .version-footer)
        const container = document.querySelector('.version-info') || 
                         document.querySelector('.version-footer') ||
                         document.querySelector('[id*="version"]');
        
        if (!container) {
            console.log('Version footer not found');
            return;
        }
        
        // Make clickable
        container.style.cursor = 'pointer';
        container.title = 'Click to copy version info';
        container.style.userSelect = 'text';
        container.style.webkitUserSelect = 'text';
        
        // Add hover effect
        container.addEventListener('mouseenter', () => {
            container.style.backgroundColor = '#e9ecef';
        });
        container.addEventListener('mouseleave', () => {
            container.style.backgroundColor = '';
        });
        
        // Copy function
        function copyVersionInfo() {
            const version = versionEl ? versionEl.textContent : 'Loading...';
            const build = buildEl ? buildEl.textContent : 'Loading...';
            const deployed = dateEl ? dateEl.textContent : 'Loading...';
            const sdk = sdkEl ? sdkEl.textContent : '10.7.1';
            
            // Format as single line (same as displayed)
            const text = `Version: ${version} | Build: ${build} | Deployed: ${deployed} | Firebase SDK: ${sdk}`;
            
            navigator.clipboard.writeText(text).then(() => {
                // Visual feedback
                const originalBg = container.style.backgroundColor;
                container.style.backgroundColor = '#d4edda';
                container.style.transition = 'background-color 0.3s';
                
                setTimeout(() => {
                    container.style.backgroundColor = originalBg || '';
                }, 500);
                
                console.log('✓ Version info copied:', text);
            }).catch(err => {
                console.error('Copy failed:', err);
                // Fallback: select text
                const range = document.createRange();
                range.selectNodeContents(container);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                alert('Version info selected. Press Ctrl+C to copy.');
            });
        }
        
        // Add click handler
        container.addEventListener('click', copyVersionInfo);
        
        // Make function globally available
        window.copyVersionInfo = copyVersionInfo;
        
        console.log('✓ Footer copy functionality initialized');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFooterCopy);
    } else {
        initFooterCopy();
    }
})();

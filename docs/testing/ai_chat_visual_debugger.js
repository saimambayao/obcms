/**
 * AI Chat Visual Position Debugger
 *
 * PURPOSE: Add visual overlays to diagnose positioning issues
 * USAGE: Copy-paste into browser console, then run: addVisualDebug()
 *
 * FEATURES:
 * - Red border: Chat panel actual position
 * - Blue border: Toggle button position
 * - Green border: Widget container
 * - Info overlay: Key metrics and viewport data
 * - Auto-removes after 10 seconds
 *
 * COMMANDS:
 * - addVisualDebug()        - Show overlays
 * - removeVisualDebug()     - Remove overlays manually
 * - addVisualDebug(30000)   - Show for 30 seconds
 */

/**
 * Add visual debugging overlay to AI chat elements
 * @param {number} duration - How long to show overlay (ms), default 10000
 */
window.addVisualDebug = function(duration = 10000) {
    console.log('🎨 Adding visual debug overlay...');

    // Remove existing overlays first
    removeVisualDebug();

    // Get elements
    const widget = document.getElementById('ai-chat-widget');
    const button = document.getElementById('ai-chat-toggle-btn');
    const panel = document.getElementById('ai-chat-panel');

    if (!widget || !button || !panel) {
        console.error('❌ Cannot add overlay: Elements not found');
        return;
    }

    // Get positions
    const widgetRect = widget.getBoundingClientRect();
    const buttonRect = button.getBoundingClientRect();
    const panelRect = panel.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    // Check visibility
    const isPanelVisible =
        panelRect.top >= 0 &&
        panelRect.bottom <= viewportHeight &&
        panelRect.left >= 0 &&
        panelRect.right <= viewportWidth;

    // Container for all overlays
    const container = document.createElement('div');
    container.id = 'ai-chat-debug-container';
    container.style.cssText = 'position: fixed; inset: 0; pointer-events: none; z-index: 999999;';

    // 1. Widget Container Overlay (Green)
    const widgetOverlay = document.createElement('div');
    widgetOverlay.className = 'debug-overlay widget-overlay';
    widgetOverlay.style.cssText = `
        position: fixed;
        top: ${widgetRect.top}px;
        left: ${widgetRect.left}px;
        width: ${widgetRect.width}px;
        height: ${widgetRect.height}px;
        border: 3px dashed #10b981;
        background: rgba(16, 185, 129, 0.05);
        pointer-events: none;
    `;

    const widgetLabel = document.createElement('div');
    widgetLabel.style.cssText = `
        position: absolute;
        top: -28px;
        left: 0;
        background: #10b981;
        color: white;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: bold;
        border-radius: 4px;
        white-space: nowrap;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    `;
    widgetLabel.textContent = `🟢 Widget Container (${Math.round(widgetRect.width)}×${Math.round(widgetRect.height)})`;
    widgetOverlay.appendChild(widgetLabel);

    // 2. Toggle Button Overlay (Blue)
    const buttonOverlay = document.createElement('div');
    buttonOverlay.className = 'debug-overlay button-overlay';
    buttonOverlay.style.cssText = `
        position: fixed;
        top: ${buttonRect.top}px;
        left: ${buttonRect.left}px;
        width: ${buttonRect.width}px;
        height: ${buttonRect.height}px;
        border: 3px dashed #3b82f6;
        background: rgba(59, 130, 246, 0.1);
        pointer-events: none;
    `;

    const buttonLabel = document.createElement('div');
    buttonLabel.style.cssText = `
        position: absolute;
        bottom: -28px;
        right: 0;
        background: #3b82f6;
        color: white;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: bold;
        border-radius: 4px;
        white-space: nowrap;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    `;
    buttonLabel.textContent = `🔵 Toggle Button`;
    buttonOverlay.appendChild(buttonLabel);

    // 3. Chat Panel Overlay (Red for hidden/error, Green for visible)
    const panelOverlay = document.createElement('div');
    const panelColor = isPanelVisible ? '#10b981' : '#ef4444';
    const panelBg = isPanelVisible ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';

    panelOverlay.className = 'debug-overlay panel-overlay';
    panelOverlay.style.cssText = `
        position: fixed;
        top: ${panelRect.top}px;
        left: ${panelRect.left}px;
        width: ${panelRect.width}px;
        height: ${panelRect.height}px;
        border: 5px dashed ${panelColor};
        background: ${panelBg};
        pointer-events: none;
    `;

    const panelLabel = document.createElement('div');
    panelLabel.style.cssText = `
        position: absolute;
        top: ${panelRect.top < 40 ? '10px' : '-38px'};
        left: 0;
        background: ${panelColor};
        color: white;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
        white-space: nowrap;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        max-width: ${panelRect.width}px;
        overflow: hidden;
        text-overflow: ellipsis;
    `;
    panelLabel.innerHTML = `
        ${isPanelVisible ? '✅' : '❌'} Chat Panel
        <small style="opacity: 0.9; margin-left: 8px;">
            ${Math.round(panelRect.top)}px from top | ${Math.round(panelRect.height)}px tall
        </small>
    `;
    panelOverlay.appendChild(panelLabel);

    // If panel is outside viewport, add arrows/indicators
    if (!isPanelVisible) {
        if (panelRect.top < 0) {
            const arrow = document.createElement('div');
            arrow.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #ef4444;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            `;
            arrow.textContent = `↑ ${Math.abs(Math.round(panelRect.top))}px ABOVE viewport`;
            panelOverlay.appendChild(arrow);
        }

        if (panelRect.bottom > viewportHeight) {
            const arrow = document.createElement('div');
            arrow.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #ef4444;
                color: white;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            `;
            arrow.textContent = `↓ ${Math.round(panelRect.bottom - viewportHeight)}px BELOW viewport`;
            panelOverlay.appendChild(arrow);
        }
    }

    // 4. Viewport Info Overlay
    const infoOverlay = document.createElement('div');
    infoOverlay.className = 'debug-overlay info-overlay';
    infoOverlay.style.cssText = `
        position: fixed;
        top: 16px;
        left: 16px;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 16px;
        font-size: 12px;
        font-family: 'Courier New', monospace;
        border-radius: 8px;
        max-width: 400px;
        pointer-events: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    `;

    const computedPanelStyle = getComputedStyle(panel);
    const isMobile = viewportWidth < 640;

    infoOverlay.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 8px;">
            <strong style="font-size: 14px;">🔍 AI Chat Debug Overlay</strong>
            <button onclick="removeVisualDebug()" style="background: #ef4444; color: white; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 11px; font-weight: bold;">✕ Close</button>
        </div>

        <div style="margin-bottom: 8px;">
            <strong>📏 Viewport:</strong> ${viewportWidth} × ${viewportHeight}px
            ${isMobile ? '<span style="background: #f59e0b; color: black; padding: 2px 6px; border-radius: 3px; margin-left: 8px; font-size: 10px;">MOBILE</span>' : '<span style="background: #10b981; color: white; padding: 2px 6px; border-radius: 3px; margin-left: 8px; font-size: 10px;">DESKTOP</span>'}
        </div>

        <div style="margin-bottom: 8px;">
            <strong>📦 Widget:</strong> ${window.getComputedStyle(widget).position} | z:${window.getComputedStyle(widget).zIndex}
            <br><small style="opacity: 0.7;">Bottom: ${window.getComputedStyle(widget).bottom} | Right: ${window.getComputedStyle(widget).right}</small>
        </div>

        <div style="margin-bottom: 8px;">
            <strong>💬 Panel:</strong> ${computedPanelStyle.position} | ${panel.classList.contains('chat-open') ? '✅ Open' : '❌ Closed'}
            <br><small style="opacity: 0.7;">Bottom: ${computedPanelStyle.bottom} | Right: ${computedPanelStyle.right}</small>
            <br><small style="opacity: 0.7;">Opacity: ${computedPanelStyle.opacity} | Visibility: ${computedPanelStyle.visibility}</small>
        </div>

        <div style="margin-bottom: 8px;">
            <strong>📐 Position:</strong>
            <br><small>Top: ${Math.round(panelRect.top)}px | Bottom: ${Math.round(panelRect.bottom)}px</small>
            <br><small>Left: ${Math.round(panelRect.left)}px | Right: ${Math.round(panelRect.right)}px</small>
        </div>

        <div style="margin-bottom: 8px;">
            <strong>📊 Dimensions:</strong>
            <br><small>Width: ${Math.round(panelRect.width)}px | Height: ${Math.round(panelRect.height)}px</small>
            <br><small>Max-Height: ${computedPanelStyle.maxHeight}</small>
        </div>

        <div style="padding: 8px; background: ${isPanelVisible ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; border-radius: 4px; border: 1px solid ${isPanelVisible ? '#10b981' : '#ef4444'};">
            <strong>${isPanelVisible ? '✅ Panel VISIBLE in viewport' : '❌ Panel NOT VISIBLE'}</strong>
            ${!isPanelVisible ? `<br><small style="margin-top: 4px; display: block;">
                ${panelRect.top < 0 ? '• Top is ' + Math.abs(Math.round(panelRect.top)) + 'px ABOVE viewport<br>' : ''}
                ${panelRect.bottom > viewportHeight ? '• Bottom is ' + Math.round(panelRect.bottom - viewportHeight) + 'px BELOW viewport<br>' : ''}
                ${panelRect.left < 0 ? '• Left is outside viewport<br>' : ''}
                ${panelRect.right > viewportWidth ? '• Right is outside viewport' : ''}
            </small>` : ''}
        </div>

        <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 10px; opacity: 0.7;">
            <strong>Legend:</strong>
            <span style="color: #10b981;">🟢 Widget</span> |
            <span style="color: #3b82f6;">🔵 Button</span> |
            <span style="color: ${isPanelVisible ? '#10b981' : '#ef4444'};">${isPanelVisible ? '✅' : '❌'} Panel</span>
            <br>
            <small>Auto-closes in ${duration / 1000}s</small>
        </div>
    `;

    // Add all overlays to container
    container.appendChild(widgetOverlay);
    container.appendChild(buttonOverlay);
    container.appendChild(panelOverlay);
    container.appendChild(infoOverlay);

    // Add to DOM
    document.body.appendChild(container);

    console.log('✅ Visual debug overlay added');
    console.log('   🟢 Green border = Widget container');
    console.log('   🔵 Blue border = Toggle button');
    console.log(`   ${isPanelVisible ? '✅ Green' : '❌ Red'} border = Chat panel`);
    console.log(`   Will auto-remove in ${duration / 1000}s`);

    // Auto-remove after duration
    window._debugOverlayTimeout = setTimeout(() => {
        removeVisualDebug();
        console.log('✅ Visual debug overlay auto-removed');
    }, duration);

    // Return info for chaining
    return {
        isPanelVisible,
        panelRect,
        widgetRect,
        buttonRect,
        viewportWidth,
        viewportHeight
    };
};

/**
 * Remove visual debugging overlays
 */
window.removeVisualDebug = function() {
    const container = document.getElementById('ai-chat-debug-container');
    if (container) {
        container.remove();
        console.log('✅ Visual debug overlay removed');
    }

    if (window._debugOverlayTimeout) {
        clearTimeout(window._debugOverlayTimeout);
        window._debugOverlayTimeout = null;
    }
};

/**
 * Add measurement lines (distance from edges)
 */
window.addMeasurementLines = function() {
    console.log('📏 Adding measurement lines...');

    removeVisualDebug(); // Remove existing overlays

    const widget = document.getElementById('ai-chat-widget');
    const panel = document.getElementById('ai-chat-panel');
    const button = document.getElementById('ai-chat-toggle-btn');

    if (!widget || !panel || !button) return;

    const widgetRect = widget.getBoundingClientRect();
    const panelRect = panel.getBoundingClientRect();
    const vh = window.innerHeight;
    const vw = window.innerWidth;

    const container = document.createElement('div');
    container.id = 'ai-chat-debug-container';
    container.style.cssText = 'position: fixed; inset: 0; pointer-events: none; z-index: 999999;';

    // Distance from widget to bottom
    const bottomLine = document.createElement('div');
    bottomLine.style.cssText = `
        position: fixed;
        left: ${widgetRect.right + 10}px;
        top: ${widgetRect.bottom}px;
        width: 2px;
        height: ${vh - widgetRect.bottom}px;
        background: linear-gradient(to bottom, #ef4444, transparent);
    `;
    const bottomLabel = document.createElement('div');
    bottomLabel.style.cssText = `
        position: fixed;
        left: ${widgetRect.right + 15}px;
        top: ${widgetRect.bottom + (vh - widgetRect.bottom) / 2}px;
        background: #ef4444;
        color: white;
        padding: 2px 6px;
        font-size: 10px;
        border-radius: 3px;
        font-family: monospace;
    `;
    bottomLabel.textContent = `${Math.round(vh - widgetRect.bottom)}px`;

    // Distance from widget to right
    const rightLine = document.createElement('div');
    rightLine.style.cssText = `
        position: fixed;
        left: ${widgetRect.right}px;
        top: ${widgetRect.top - 10}px;
        width: ${vw - widgetRect.right}px;
        height: 2px;
        background: linear-gradient(to right, #3b82f6, transparent);
    `;
    const rightLabel = document.createElement('div');
    rightLabel.style.cssText = `
        position: fixed;
        left: ${widgetRect.right + (vw - widgetRect.right) / 2}px;
        top: ${widgetRect.top - 25}px;
        background: #3b82f6;
        color: white;
        padding: 2px 6px;
        font-size: 10px;
        border-radius: 3px;
        font-family: monospace;
    `;
    rightLabel.textContent = `${Math.round(vw - widgetRect.right)}px`;

    container.appendChild(bottomLine);
    container.appendChild(bottomLabel);
    container.appendChild(rightLine);
    container.appendChild(rightLabel);

    document.body.appendChild(container);

    console.log('✅ Measurement lines added');
    setTimeout(() => removeVisualDebug(), 5000);
};

// Global notification
console.log('✅ AI Chat Visual Debugger loaded');
console.log('📋 Available commands:');
console.log('   - addVisualDebug()           Show debug overlay (10s)');
console.log('   - addVisualDebug(30000)      Show debug overlay (30s)');
console.log('   - removeVisualDebug()        Remove overlay');
console.log('   - addMeasurementLines()      Show distance measurements');

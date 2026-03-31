// Serial Monitor Application
class SerialMonitor {
    constructor() {
        this.port = null;
        this.reader = null;
        this.writer = null;
        this.readableStreamClosed = null;
        this.writableStreamClosed = null;
        this.isReading = false;
        this.rxBytes = 0;
        this.txBytes = 0;
        this.lineCount = 0;
        this.decoder = new TextDecoder();
        this.encoder = new TextEncoder();
        this.buffer = '';

        // Initialize DOM elements
        this.initElements();
        this.initEventListeners();
        this.loadSettings();
        this.checkWebSerialSupport();
    }

    initElements() {
        // Connection controls
        this.connectBtn = document.getElementById('connectBtn');
        this.disconnectBtn = document.getElementById('disconnectBtn');
        this.baudRateSelect = document.getElementById('baudRate');

        // Settings
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.clearBtn = document.getElementById('clearBtn');

        // Monitor output
        this.monitorOutput = document.getElementById('monitorOutput');
        this.autoScrollCheckbox = document.getElementById('autoScroll');
        this.showTimestampCheckbox = document.getElementById('showTimestamp');
        this.hexModeCheckbox = document.getElementById('hexMode');
        this.filterInput = document.getElementById('filterInput');

        // Input area
        this.sendInput = document.getElementById('sendInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.lineEndingSelect = document.getElementById('lineEnding');

        // Status bar
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.rxBytesSpan = document.getElementById('rxBytes');
        this.txBytesSpan = document.getElementById('txBytes');
        this.lineCountSpan = document.getElementById('lineCount');

        // Style settings
        this.fontSizeInput = document.getElementById('fontSize');
        this.fontSizeValue = document.getElementById('fontSizeValue');
        this.lineHeightInput = document.getElementById('lineHeight');
        this.lineHeightValue = document.getElementById('lineHeightValue');
        this.normalColorInput = document.getElementById('normalColor');
        this.errorColorInput = document.getElementById('errorColor');
        this.warningColorInput = document.getElementById('warningColor');
        this.infoColorInput = document.getElementById('infoColor');
        this.debugColorInput = document.getElementById('debugColor');
        this.bgColorInput = document.getElementById('bgColor');
        this.maxLinesInput = document.getElementById('maxLines');
        this.themePresets = document.querySelectorAll('.theme-preset');
    }

    initEventListeners() {
        // Connection
        this.connectBtn.addEventListener('click', () => this.connect());
        this.disconnectBtn.addEventListener('click', () => this.disconnect());

        // Settings
        this.settingsBtn.addEventListener('click', () => this.toggleSettings());
        this.clearBtn.addEventListener('click', () => this.clearOutput());

        // Sending data
        this.sendBtn.addEventListener('click', () => this.sendData());
        this.sendInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendData();
        });

        // Style settings
        this.fontSizeInput.addEventListener('input', (e) => {
            this.fontSizeValue.textContent = e.target.value;
            this.monitorOutput.style.fontSize = e.target.value + 'px';
            this.saveSettings();
        });

        this.lineHeightInput.addEventListener('input', (e) => {
            this.lineHeightValue.textContent = e.target.value;
            this.monitorOutput.style.lineHeight = e.target.value;
            this.saveSettings();
        });

        this.normalColorInput.addEventListener('input', (e) => {
            this.monitorOutput.style.color = e.target.value;
            this.saveSettings();
        });

        this.errorColorInput.addEventListener('input', () => this.updateLogColors());
        this.warningColorInput.addEventListener('input', () => this.updateLogColors());
        this.infoColorInput.addEventListener('input', () => this.updateLogColors());
        this.debugColorInput.addEventListener('input', () => this.updateLogColors());

        this.bgColorInput.addEventListener('input', (e) => {
            this.monitorOutput.style.backgroundColor = e.target.value;
            this.saveSettings();
        });

        this.maxLinesInput.addEventListener('change', () => this.saveSettings());

        // Theme presets
        this.themePresets.forEach(preset => {
            preset.addEventListener('click', (e) => {
                this.applyThemePreset(e.target.dataset.theme);
            });
        });

        // Filter
        this.filterInput.addEventListener('input', () => this.applyFilter());
    }

    checkWebSerialSupport() {
        if (!('serial' in navigator)) {
            this.addLog('Web Serial API is not supported in this browser. Please use Chrome, Edge, or Opera.', 'error');
            this.connectBtn.disabled = true;
        }
    }

    async connect() {
        try {
            // Request port
            this.port = await navigator.serial.requestPort();

            // Get baud rate
            const baudRate = parseInt(this.baudRateSelect.value);

            // Open port
            await this.port.open({ baudRate });

            // Update UI
            this.updateConnectionStatus(true);
            this.addLog(`Connected at ${baudRate} baud`, 'info');

            // Start reading
            this.startReading();

        } catch (error) {
            this.addLog(`Connection error: ${error.message}`, 'error');
            console.error('Connection error:', error);
        }
    }

    async disconnect() {
        try {
            // Stop reading
            this.isReading = false;

            if (this.reader) {
                await this.reader.cancel();
                await this.readableStreamClosed.catch(() => {});
                this.reader = null;
            }

            if (this.writer) {
                await this.writer.close();
                await this.writableStreamClosed.catch(() => {});
                this.writer = null;
            }

            // Close port
            if (this.port) {
                await this.port.close();
                this.port = null;
            }

            this.updateConnectionStatus(false);
            this.addLog('Disconnected', 'warning');

        } catch (error) {
            this.addLog(`Disconnect error: ${error.message}`, 'error');
            console.error('Disconnect error:', error);
        }
    }

    async startReading() {
        this.isReading = true;

        try {
            const reader = this.port.readable.getReader();
            this.reader = reader;
            this.readableStreamClosed = this.port.readable.cancel();

            while (this.isReading && this.port.readable) {
                const { value, done } = await reader.read();
                if (done) break;

                if (value) {
                    this.rxBytes += value.length;
                    this.updateStats();

                    if (this.hexModeCheckbox.checked) {
                        this.processHexData(value);
                    } else {
                        this.processTextData(value);
                    }
                }
            }
        } catch (error) {
            if (error.name !== 'NetworkError') {
                this.addLog(`Read error: ${error.message}`, 'error');
                console.error('Read error:', error);
            }
        } finally {
            if (this.reader) {
                this.reader.releaseLock();
            }
        }
    }

    processTextData(data) {
        const text = this.decoder.decode(data);
        this.buffer += text;

        // Split by newlines
        const lines = this.buffer.split('\n');

        // Keep the last incomplete line in the buffer
        this.buffer = lines.pop();

        // Process complete lines
        lines.forEach(line => {
            if (line.trim() || line.includes('\r')) {
                // Remove carriage returns
                line = line.replace(/\r/g, '');
                if (line.trim()) {
                    this.addLog(line, this.detectLogLevel(line));
                }
            }
        });
    }

    processHexData(data) {
        const hexString = Array.from(data)
            .map(byte => byte.toString(16).padStart(2, '0').toUpperCase())
            .join(' ');

        this.addLog(hexString, 'normal');
    }

    detectLogLevel(text) {
        const lower = text.toLowerCase();

        if (lower.includes('error') || lower.includes('err:') || lower.includes('failed')) {
            return 'error';
        } else if (lower.includes('warning') || lower.includes('warn:')) {
            return 'warning';
        } else if (lower.includes('info:') || lower.includes('[i]')) {
            return 'info';
        } else if (lower.includes('debug') || lower.includes('dbg:')) {
            return 'debug';
        }

        return 'normal';
    }

    addLog(text, level = 'normal') {
        const line = document.createElement('div');
        line.className = `log-line ${level}`;

        // Add timestamp if enabled
        if (this.showTimestampCheckbox.checked) {
            const timestamp = document.createElement('span');
            timestamp.className = 'timestamp';
            timestamp.textContent = new Date().toLocaleTimeString() + '.' + String(new Date().getMilliseconds()).padStart(3, '0');
            line.appendChild(timestamp);
        }

        // Add text
        const textSpan = document.createElement('span');
        textSpan.textContent = text;
        line.appendChild(textSpan);

        // Apply custom colors
        this.applyLineColors(line, level);

        // Add to output
        this.monitorOutput.appendChild(line);

        // Update line count
        this.lineCount++;
        this.updateStats();

        // Limit max lines
        const maxLines = parseInt(this.maxLinesInput.value);
        if (maxLines > 0) {
            const lines = this.monitorOutput.querySelectorAll('.log-line');
            if (lines.length > maxLines) {
                lines[0].remove();
                this.lineCount--;
            }
        }

        // Apply filter
        if (this.filterInput.value) {
            const filterText = this.filterInput.value.toLowerCase();
            if (!text.toLowerCase().includes(filterText)) {
                line.style.display = 'none';
            }
        }

        // Auto-scroll
        if (this.autoScrollCheckbox.checked) {
            this.monitorOutput.scrollTop = this.monitorOutput.scrollHeight;
        }
    }

    applyLineColors(line, level) {
        switch (level) {
            case 'error':
                line.style.color = this.errorColorInput.value;
                break;
            case 'warning':
                line.style.color = this.warningColorInput.value;
                break;
            case 'info':
                line.style.color = this.infoColorInput.value;
                break;
            case 'debug':
                line.style.color = this.debugColorInput.value;
                break;
        }
    }

    updateLogColors() {
        document.querySelectorAll('.log-line.error').forEach(line => {
            line.style.color = this.errorColorInput.value;
        });
        document.querySelectorAll('.log-line.warning').forEach(line => {
            line.style.color = this.warningColorInput.value;
        });
        document.querySelectorAll('.log-line.info').forEach(line => {
            line.style.color = this.infoColorInput.value;
        });
        document.querySelectorAll('.log-line.debug').forEach(line => {
            line.style.color = this.debugColorInput.value;
        });
        this.saveSettings();
    }

    async sendData() {
        if (!this.port || !this.sendInput.value) return;

        try {
            // Get or create writer
            if (!this.writer) {
                this.writer = this.port.writable.getWriter();
                this.writableStreamClosed = this.port.writable.close();
            }

            // Prepare data
            let data = this.sendInput.value;
            const lineEnding = this.lineEndingSelect.value;

            // Add line ending
            if (lineEnding) {
                data += lineEnding.replace('\\n', '\n').replace('\\r', '\r');
            }

            // Encode and send
            const encoded = this.encoder.encode(data);
            await this.writer.write(encoded);

            this.txBytes += encoded.length;
            this.updateStats();

            // Add to log
            this.addLog(`> ${this.sendInput.value}`, 'info');

            // Clear input
            this.sendInput.value = '';
            this.sendInput.focus();

        } catch (error) {
            this.addLog(`Send error: ${error.message}`, 'error');
            console.error('Send error:', error);
        }
    }

    clearOutput() {
        this.monitorOutput.innerHTML = '';
        this.lineCount = 0;
        this.updateStats();
        this.addLog('Output cleared', 'info');
    }

    toggleSettings() {
        this.settingsPanel.classList.toggle('active');
    }

    applyFilter() {
        const filterText = this.filterInput.value.toLowerCase();
        const lines = this.monitorOutput.querySelectorAll('.log-line');

        lines.forEach(line => {
            if (!filterText || line.textContent.toLowerCase().includes(filterText)) {
                line.style.display = '';
            } else {
                line.style.display = 'none';
            }
        });
    }

    applyThemePreset(theme) {
        // Update active state
        this.themePresets.forEach(preset => {
            preset.classList.remove('active');
            if (preset.dataset.theme === theme) {
                preset.classList.add('active');
            }
        });

        // Remove all theme classes
        this.monitorOutput.classList.remove('theme-dark', 'theme-light', 'theme-terminal');

        switch (theme) {
            case 'dark':
                this.monitorOutput.classList.add('theme-dark');
                this.bgColorInput.value = '#1e1e1e';
                this.normalColorInput.value = '#d4d4d4';
                break;

            case 'light':
                this.monitorOutput.classList.add('theme-light');
                this.bgColorInput.value = '#ffffff';
                this.normalColorInput.value = '#000000';
                break;

            case 'terminal':
                this.monitorOutput.classList.add('theme-terminal');
                this.bgColorInput.value = '#000000';
                this.normalColorInput.value = '#00ff00';
                break;
        }

        this.monitorOutput.style.backgroundColor = this.bgColorInput.value;
        this.monitorOutput.style.color = this.normalColorInput.value;
        this.saveSettings();
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.connectBtn.disabled = true;
            this.disconnectBtn.disabled = false;
            this.sendInput.disabled = false;
            this.sendBtn.disabled = false;
            this.statusIndicator.classList.remove('disconnected');
            this.statusIndicator.classList.add('connected');
            this.statusText.textContent = 'Connected';
        } else {
            this.connectBtn.disabled = false;
            this.disconnectBtn.disabled = true;
            this.sendInput.disabled = true;
            this.sendBtn.disabled = true;
            this.statusIndicator.classList.remove('connected');
            this.statusIndicator.classList.add('disconnected');
            this.statusText.textContent = 'Disconnected';
        }
    }

    updateStats() {
        this.rxBytesSpan.textContent = this.rxBytes.toLocaleString();
        this.txBytesSpan.textContent = this.txBytes.toLocaleString();
        this.lineCountSpan.textContent = this.lineCount.toLocaleString();
    }

    saveSettings() {
        const settings = {
            fontSize: this.fontSizeInput.value,
            lineHeight: this.lineHeightInput.value,
            normalColor: this.normalColorInput.value,
            errorColor: this.errorColorInput.value,
            warningColor: this.warningColorInput.value,
            infoColor: this.infoColorInput.value,
            debugColor: this.debugColorInput.value,
            bgColor: this.bgColorInput.value,
            maxLines: this.maxLinesInput.value,
            baudRate: this.baudRateSelect.value,
            autoScroll: this.autoScrollCheckbox.checked,
            showTimestamp: this.showTimestampCheckbox.checked,
            lineEnding: this.lineEndingSelect.value
        };

        localStorage.setItem('serialMonitorSettings', JSON.stringify(settings));
    }

    loadSettings() {
        const saved = localStorage.getItem('serialMonitorSettings');
        if (!saved) return;

        try {
            const settings = JSON.parse(saved);

            if (settings.fontSize) {
                this.fontSizeInput.value = settings.fontSize;
                this.fontSizeValue.textContent = settings.fontSize;
                this.monitorOutput.style.fontSize = settings.fontSize + 'px';
            }

            if (settings.lineHeight) {
                this.lineHeightInput.value = settings.lineHeight;
                this.lineHeightValue.textContent = settings.lineHeight;
                this.monitorOutput.style.lineHeight = settings.lineHeight;
            }

            if (settings.normalColor) {
                this.normalColorInput.value = settings.normalColor;
                this.monitorOutput.style.color = settings.normalColor;
            }

            if (settings.errorColor) this.errorColorInput.value = settings.errorColor;
            if (settings.warningColor) this.warningColorInput.value = settings.warningColor;
            if (settings.infoColor) this.infoColorInput.value = settings.infoColor;
            if (settings.debugColor) this.debugColorInput.value = settings.debugColor;

            if (settings.bgColor) {
                this.bgColorInput.value = settings.bgColor;
                this.monitorOutput.style.backgroundColor = settings.bgColor;
            }

            if (settings.maxLines) this.maxLinesInput.value = settings.maxLines;
            if (settings.baudRate) this.baudRateSelect.value = settings.baudRate;

            if (settings.autoScroll !== undefined) {
                this.autoScrollCheckbox.checked = settings.autoScroll;
            }

            if (settings.showTimestamp !== undefined) {
                this.showTimestampCheckbox.checked = settings.showTimestamp;
            }

            if (settings.lineEnding) this.lineEndingSelect.value = settings.lineEnding;

        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
}

// Initialize the application when DOM is ready
let monitor;

document.addEventListener('DOMContentLoaded', () => {
    monitor = new SerialMonitor();
});

// Handle page unload
window.addEventListener('beforeunload', async () => {
    if (monitor && monitor.port) {
        await monitor.disconnect();
    }
});

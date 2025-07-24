// Import configuration schema
const CONFIG_FIELDS = window.CONFIG_SCHEMA;

// Process state tracking
let isProcessRunning = false;
let buttonManager;
let loadingOverlay;

// Auto-save functionality with debouncing
let saveTimeout;
const SAVE_DELAY = 500;
let isSettingValues = false;

// Console management
const consoleContent = document.getElementById('console-content');
const MAX_CONSOLE_LINES = 512;
let consoleLineCount = 0;

// Button management system
class ButtonManager {
    constructor() {
        this.buttons = {
            start: document.getElementById('start-process'),
            stop: document.getElementById('stop-process'),
            setupVenv: document.getElementById('setup-venv'),
            resetVenv: document.getElementById('reset-venv'),
            refreshMicrophones: document.getElementById('refresh-microphones')
        };

        // Initialize button states - process is not running at startup
        this.setProcessStopped();
    }

    setState(buttonName, disabled) {
        const button = this.buttons[buttonName];
        if (!button) return;

        button.disabled = disabled;
    }

    setProcessRunning() {
        this.setState('start', true);
        this.setState('stop', false);
        isProcessRunning = true;
    }

    setProcessStopped() {
        this.setState('start', false);
        this.setState('stop', true);
        isProcessRunning = false;
    }

    async withButtonLoading(buttonName, asyncFn) {
        this.setState(buttonName, true);
        try {
            return await asyncFn();
        } finally {
            this.setState(buttonName, false);
        }
    }
}

// Add loading overlay management
class LoadingOverlay {
    constructor() {
        this.overlay = document.getElementById('loading-overlay');
        this.form = document.getElementById('config-form');
        this.messageElement = this.overlay.querySelector('p');
        this.defaultMessage = 'Environment setup underway - please wait.';
        this.originalStates = new Map(); // Track original disabled states
    }

    show(message = null) {
        this.messageElement.textContent = message || this.defaultMessage;
        this.overlay.classList.remove('hidden');
        // Disable all form inputs and buttons in the entire left panel
        const leftPanel = this.overlay.parentElement;
        const inputs = leftPanel.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            // Store original disabled state before disabling
            this.originalStates.set(input, input.disabled);
            input.disabled = true;
            input.classList.add('opacity-50');
        });
    }

    hide() {
        this.overlay.classList.add('hidden');
        // Restore original states of form inputs and buttons
        const leftPanel = this.overlay.parentElement;
        const inputs = leftPanel.querySelectorAll('input, select, textarea, button');
        inputs.forEach(input => {
            // Restore original disabled state
            input.disabled = this.originalStates.get(input) || false;
            input.classList.remove('opacity-50');
        });
        // Clear the stored states
        this.originalStates.clear();
        // Reset to default message
        this.messageElement.textContent = this.defaultMessage;
    }
}

// Handle status messages with better color management
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;

    // Remove all status classes
    const statusClasses = ['hidden', 'bg-green-100', 'bg-red-100', 'bg-blue-100', 'text-green-800', 'text-red-800', 'text-blue-800'];
    statusEl.classList.remove(...statusClasses);

    // Add appropriate classes based on type
    const typeMap = {
        success: ['bg-green-100', 'text-green-800'],
        error: ['bg-red-100', 'text-red-800'],
        info: ['bg-blue-100', 'text-blue-800']
    };

    statusEl.classList.add(...(typeMap[type] || typeMap.info));

    // Also log to console
    appendToConsole(message, type === 'error' ? 'stderr' : 'info');

    setTimeout(() => statusEl.classList.add('hidden'), 5000);
}

// Get form values using field mappings
function getFormValues() {
    const config = {};

    for (const [fieldName, fieldConfig] of Object.entries(CONFIG_FIELDS)) {
        const element = document.getElementById(fieldName);
        if (!element) continue;

        switch (fieldConfig.type) {
            case 'boolean':
                config[fieldName] = element.checked ? 1 : 0;
                break;
            case 'number':
                const numValue = parseInt(element.value);
                config[fieldName] = isNaN(numValue) ? fieldConfig.default : numValue;
                break;
            case 'text':
                config[fieldName] = element.value || fieldConfig.default;
                break;
            default:
                config[fieldName] = element.value || fieldConfig.default;
        }
    }

    return config;
}

// Set form values using field mappings
function setFormValues(config) {
    isSettingValues = true; // Disable auto-save temporarily

    for (const [fieldName, fieldConfig] of Object.entries(CONFIG_FIELDS)) {
        const element = document.getElementById(fieldName);
        if (!element) continue;

        const value = config[fieldName] ?? fieldConfig.default;

        switch (fieldConfig.type) {
            case 'boolean':
                element.checked = value === 1;
                break;
            case 'text':
                element.value = value || '';
                break;
            default:
                element.value = value;
        }
    }

    // Handle use_builtin toggle state
    const useBuiltin = config.use_builtin === 1;
    const customChatboxInputs = ['block_width', 'num_blocks', 'rows', 'cols'];
    customChatboxInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.disabled = useBuiltin;
            if (useBuiltin) {
                input.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                input.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }
    });

    // Update volume display
    if (config.volume !== undefined) {
        const volumePercent = Math.round(config.volume);
        document.getElementById('volume-display').textContent = `${volumePercent}%`;
    }

    isSettingValues = false; // Re-enable auto-save
}

function appendToConsole(message, type = 'stdout') {
    const timestamp = new Date().toLocaleTimeString();
    const timestampSpan = document.createElement('span');
    timestampSpan.className = 'console-timestamp';
    timestampSpan.textContent = `[${timestamp}] `;

    const messageSpan = document.createElement('span');
    messageSpan.className = `console-${type}`;
    messageSpan.textContent = message;

    const lineDiv = document.createElement('div');
    lineDiv.appendChild(timestampSpan);
    lineDiv.appendChild(messageSpan);

    consoleContent.appendChild(lineDiv);
    consoleLineCount++;

    // Remove old lines if we exceed the limit
    if (consoleLineCount > MAX_CONSOLE_LINES) {
        // Calculate how many lines to remove (remove 10% to avoid frequent trimming)
        const linesToRemove = Math.floor(MAX_CONSOLE_LINES * 0.1);

        // Remove the oldest lines
        for (let i = 0; i < linesToRemove; i++) {
            if (consoleContent.firstChild) {
                consoleContent.removeChild(consoleContent.firstChild);
            }
        }

        consoleLineCount -= linesToRemove;

        // Add a notice that lines were trimmed
        const trimNotice = document.createElement('div');
        trimNotice.className = 'console-info';
        trimNotice.innerHTML = '<span class="console-timestamp">[System] </span><span class="console-info">... older lines removed to maintain performance ...</span>';
        consoleContent.insertBefore(trimNotice, consoleContent.firstChild);
    }

    // Auto-scroll to bottom
    const pythonConsole = document.getElementById('python-console');
    pythonConsole.scrollTop = pythonConsole.scrollHeight;
}

// Async action handler with better error handling
async function handleAsyncAction(actionName, actionFn) {
    try {
        const result = await actionFn();
        if (result?.message) {
            showStatus(result.message, 'success');
        }
        return result;
    } catch (error) {
        showStatus(`${actionName} failed: ${error.message}`, 'error');
        throw error;
    }
}

async function autoSaveConfig() {
    if (isSettingValues) return;

    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(async () => {
        try {
            const config = getFormValues();
            await window.electronAPI.saveConfig(config);
            showStatus('Configuration saved', 'success');

            // Restart process if running
            if (isProcessRunning) {
                appendToConsole('Restarting process with new configuration...', 'info');

                try {
                    await window.electronAPI.stopProcess();
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    await window.electronAPI.startProcess();
                    buttonManager.setProcessRunning();
                    appendToConsole('Process restarted with new configuration', 'info');
                } catch (error) {
                    appendToConsole(`Failed to restart process: ${error.message}`, 'stderr');
                    buttonManager.setProcessStopped();
                }
            }
        } catch (error) {
            showStatus(`Failed to save configuration: ${error.message}`, 'error');
        }
    }, SAVE_DELAY);
}

// Auto-save setup
function setupAutoSave() {
    const form = document.getElementById('config-form');
    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        const eventType = input.type === 'checkbox' ? 'change' :
                         (input.type === 'number' || input.type === 'text' || input.tagName === 'TEXTAREA') ? 'input' : 'change';
        input.addEventListener(eventType, autoSaveConfig);
    });
}

// Microphone loading
async function loadMicrophones() {
    const microphoneSelect = document.getElementById('microphone');

    try {
        // Check/install requirements during startup
        appendToConsole('Checking virtual environment and requirements...', 'info');
        loadingOverlay.show('Setting up environment - this can take several minutes.');
        try {
            await handleAsyncAction('Install requirements', () => window.electronAPI.installRequirements());
        } finally {
            loadingOverlay.hide(); // Always hide overlay when done
        }

        appendToConsole('Loading available microphones...', 'info');
        const microphones = await window.electronAPI.getMicrophones();

        microphoneSelect.innerHTML = '';

        if (microphones.length === 0) {
            microphoneSelect.innerHTML = '<option value="" disabled>No microphones found</option>';
            appendToConsole('No microphones found', 'stderr');
            return;
        }

        appendToConsole(`Found ${microphones.length} microphone(s)`, 'info');
        microphones.forEach(mic => {
            const option = document.createElement('option');
            option.value = mic.index.toString();
            option.textContent = mic.name;
            microphoneSelect.appendChild(option);
            appendToConsole(`  - ${mic.name} (Device ${mic.index})`, 'stdout');
        });

        // Restore previously selected microphone
        try {
            const config = await window.electronAPI.loadConfig();
            if (config.microphone) {
                microphoneSelect.value = config.microphone;
            }
        } catch (error) {
            // Ignore config load errors here
        }

    } catch (error) {
        appendToConsole(`Failed to load microphones: ${error.message}`, 'stderr');
        microphoneSelect.innerHTML = '<option value="" disabled>Error loading microphones</option>';
    }
}

// Event handlers setup
function setupEventHandlers() {
    // Advanced settings toggle
    document.getElementById('toggle-advanced').addEventListener('click', () => {
        const advancedSettings = document.getElementById('advanced-settings');
        const chevron = document.getElementById('chevron');

        if (advancedSettings.classList.contains('hidden')) {
            advancedSettings.classList.remove('hidden');
            chevron.classList.add('rotate-90');
        } else {
            advancedSettings.classList.add('hidden');
            chevron.classList.remove('rotate-90');
        }
    });

    // Use builtin chatbox toggle
    document.getElementById('use_builtin').addEventListener('change', (e) => {
        const customChatboxInputs = ['block_width', 'num_blocks', 'rows', 'cols'];
        const isBuiltin = e.target.checked;

        customChatboxInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.disabled = isBuiltin;
                if (isBuiltin) {
                    input.classList.add('opacity-50', 'cursor-not-allowed');
                } else {
                    input.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            }
        });
    });

    // Volume slider update
    document.getElementById('volume').addEventListener('input', (e) => {
        const volumePercent = Math.round(e.target.value);
        document.getElementById('volume-display').textContent = `${volumePercent}%`;
    });

    // Setup virtual environment
    document.getElementById('setup-venv').addEventListener('click', async () => {
        loadingOverlay.show('Setting up virtual environment - please wait...'); // Show overlay with custom message
        try {
            await buttonManager.withButtonLoading('setupVenv', async () => {
                await window.electronAPI.deleteVenvIndicatorFile();
                await handleAsyncAction('Install requirements', () => window.electronAPI.installRequirements());
            });
        } finally {
            loadingOverlay.hide(); // Always hide overlay when done
        }
    });

    // Reset virtual environment
    document.getElementById('reset-venv').addEventListener('click', async () => {
        loadingOverlay.show('Resetting virtual environment - please wait...'); // Show overlay with custom message
        try {
            await buttonManager.withButtonLoading('resetVenv', async () => {
                await handleAsyncAction('Reset virtual environment', () => window.electronAPI.resetVenv());
            });
        } finally {
            loadingOverlay.hide(); // Always hide overlay when done
        }
    });

    // Reset configuration
    document.getElementById('reset-config').addEventListener('click', async () => {
        const confirmReset = confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.');
        if (!confirmReset) return;

        try {
            // Stop process if running
            const wasRunning = isProcessRunning;
            if (wasRunning) {
                appendToConsole('Stopping process before resetting configuration...', 'info');
                await window.electronAPI.stopProcess();
                buttonManager.setProcessStopped();
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // Reset configuration
            appendToConsole('Resetting configuration to defaults...', 'info');
            const result = await window.electronAPI.resetConfig();

            // Reload configuration with defaults
            const config = await window.electronAPI.loadConfig();
            setFormValues(config);

            showStatus(result.message, 'success');
            appendToConsole('Configuration reset successfully', 'info');

            // Restart process if it was running
            if (wasRunning) {
                appendToConsole('Restarting process with default configuration...', 'info');
                await window.electronAPI.startProcess();
                buttonManager.setProcessRunning();
                appendToConsole('Process restarted with default configuration', 'info');
            }
        } catch (error) {
            showStatus(`Failed to reset configuration: ${error.message}`, 'error');
            appendToConsole(`Failed to reset configuration: ${error.message}`, 'stderr');
        }
    });

    // Refresh microphones
    document.getElementById('refresh-microphones').addEventListener('click', async () => {
        await buttonManager.withButtonLoading('refreshMicrophones', async () => {
            await loadMicrophones();
        });
    });

    // Start process
    document.getElementById('start-process').addEventListener('click', async () => {
        buttonManager.setState('start', true);

        try {
            // The installRequirements function will now check if venv is set up.
            loadingOverlay.show('Verifying environment setup - please wait...'); // Show overlay with custom message
            try {
                await window.electronAPI.installRequirements();
                appendToConsole('Virtual environment setup checked/completed', 'info');
            } finally {
                loadingOverlay.hide(); // Always hide overlay when done
            }

            await window.electronAPI.startProcess();
            buttonManager.setProcessRunning();
            appendToConsole('Process started successfully', 'info');
        } catch (error) {
            appendToConsole(`Failed to start process: ${error.message}`, 'stderr');
            buttonManager.setState('start', false);
        }
    });

    // Stop process
    document.getElementById('stop-process').addEventListener('click', async () => {
        buttonManager.setState('stop', true);

        try {
            await window.electronAPI.stopProcess();
            appendToConsole('Process stop initiated', 'info');
        } catch (error) {
            appendToConsole(`Failed to stop process: ${error.message}`, 'stderr');
            buttonManager.setState('stop', false);
        }
    });

    // Listen for process stopped event
    window.electronAPI.onProcessStopped(() => {
        buttonManager.setProcessStopped();
    });
}

// Initialize application
window.addEventListener('load', async () => {
    appendToConsole('TaSTT Configuration UI initialized', 'info');

    loadingOverlay = new LoadingOverlay();
    buttonManager = new ButtonManager();

    // Set up Python output listener first so we capture all output
    window.electronAPI.onPythonOutput((data) => {
        appendToConsole(data.message, data.type);
    });

    // Load configuration
    try {
        const config = await window.electronAPI.loadConfig();
        setFormValues(config);
        appendToConsole('Configuration loaded', 'info');
    } catch (error) {
        appendToConsole(`Failed to load configuration: ${error.message}`, 'stderr');
    }

    // Load microphones
    await loadMicrophones();

    // Setup event handlers and auto-save
    setupEventHandlers();
    setupAutoSave();
});

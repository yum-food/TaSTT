// Handle status messages
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.classList.remove('hidden', 'bg-green-100', 'bg-red-100', 'bg-blue-100', 'text-green-800', 'text-red-800', 'text-blue-800');
    
    if (type === 'success') {
        statusEl.classList.add('bg-green-100', 'text-green-800');
    } else if (type === 'error') {
        statusEl.classList.add('bg-red-100', 'text-red-800');
    } else {
        statusEl.classList.add('bg-blue-100', 'text-blue-800');
    }
    
    // Also log to console
    appendToConsole(message, type === 'error' ? 'stderr' : 'info');
    
    setTimeout(() => {
        statusEl.classList.add('hidden');
    }, 5000);
}

// Get form values
function getFormValues() {
    const microphoneValue = document.getElementById('microphone').value;
    // Convert to number if it's a numeric string (device index)
    const microphoneForConfig = /^\d+$/.test(microphoneValue) ? parseInt(microphoneValue) : microphoneValue;
    
    return {
        compute_type: document.getElementById('compute_type').value,
        enable_debug_mode: document.getElementById('enable_debug_mode').checked ? 1 : 0,
        enable_previews: document.getElementById('enable_previews').checked ? 1 : 0,
        save_audio: document.getElementById('save_audio').checked ? 1 : 0,
        language: document.getElementById('language').value,
        gpu_idx: parseInt(document.getElementById('gpu_idx').value),
        max_speech_duration_s: parseInt(document.getElementById('max_speech_duration_s').value),
        min_silence_duration_ms: parseInt(document.getElementById('min_silence_duration_ms').value),
        microphone: microphoneForConfig,
        model: document.getElementById('model').value,
        reset_after_silence_s: parseInt(document.getElementById('reset_after_silence_s').value),
        transcription_loop_delay_ms: parseInt(document.getElementById('transcription_loop_delay_ms').value),
        use_cpu: document.getElementById('use_cpu').checked ? 1 : 0,
        block_width: parseInt(document.getElementById('block_width').value),
        num_blocks: parseInt(document.getElementById('num_blocks').value),
        rows: parseInt(document.getElementById('rows').value),
        cols: parseInt(document.getElementById('cols').value)
    };
}

// Add a flag to prevent auto-save during programmatic updates
let isSettingValues = false;

// Set form values
function setFormValues(config) {
    isSettingValues = true; // Disable auto-save temporarily
    
    document.getElementById('compute_type').value = config.compute_type || 'int8';
    document.getElementById('enable_debug_mode').checked = config.enable_debug_mode === 1;
    document.getElementById('enable_previews').checked = config.enable_previews === 1;
    document.getElementById('save_audio').checked = config.save_audio === 1;
    document.getElementById('language').value = config.language || 'english';
    document.getElementById('gpu_idx').value = config.gpu_idx || 0;
    document.getElementById('max_speech_duration_s').value = config.max_speech_duration_s || 10;
    document.getElementById('min_silence_duration_ms').value = config.min_silence_duration_ms || 250;
    document.getElementById('microphone').value = config.microphone || 'motu';
    document.getElementById('model').value = config.model || 'turbo';
    document.getElementById('reset_after_silence_s').value = config.reset_after_silence_s || 15;
    document.getElementById('transcription_loop_delay_ms').value = config.transcription_loop_delay_ms || 100;
    document.getElementById('use_cpu').checked = config.use_cpu === 1;
    document.getElementById('block_width').value = config.block_width || 2;
    document.getElementById('num_blocks').value = config.num_blocks || 40;
    document.getElementById('rows').value = config.rows || 10;
    document.getElementById('cols').value = config.cols || 24;
    
    isSettingValues = false; // Re-enable auto-save
}

// Toggle advanced settings
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

// Simplify button handlers by extracting common patterns
async function handleAsyncAction(actionName, actionFn) {
    try {
        const result = await actionFn();
        if (result && result.message) {
            showStatus(result.message, 'success');
        }
        return result;
    } catch (error) {
        showStatus(`${actionName} failed: ${error.message}`, 'error');
        throw error;
    }
}

// Process control buttons
const startButton = document.getElementById('start-process');
const stopButton = document.getElementById('stop-process');

// Helper functions for button state management
function setButtonState(button, disabled) {
    button.disabled = disabled;
    if (disabled) {
        button.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        button.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function setProcessRunningState() {
    setButtonState(startButton, true);
    setButtonState(stopButton, false);
}

function setProcessStoppedState() {
    setButtonState(startButton, false);
    setButtonState(stopButton, true);
}

// Auto-save functionality with debouncing
let saveTimeout;
const SAVE_DELAY = 500; // milliseconds

async function autoSaveConfig() {
    if (isSettingValues) return; // Don't save during programmatic updates
    
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(async () => {
        try {
            const config = getFormValues();
            await window.electronAPI.saveConfig(config);
            showStatus('Configuration saved', 'success');
            
            // Check if process is running (stop button is enabled means process is running)
            const stopButton = document.getElementById('stop-process');
            
            if (!stopButton.disabled) {
                // Process is running, restart it with new config
                appendToConsole('Restarting process with new configuration...', 'info');
                
                try {
                    await window.electronAPI.stopProcess();
                    
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                    await window.electronAPI.startProcess();
                    
                    // Update button states to reflect running process
                    setProcessRunningState();
                    
                    appendToConsole('Process restarted with new configuration', 'info');
                } catch (error) {
                    appendToConsole(`Failed to restart process: ${error.message}`, 'stderr');
                    // Process is stopped, update button states
                    setProcessStoppedState();
                }
            }
        } catch (error) {
            showStatus(`Failed to save configuration: ${error.message}`, 'error');
        }
    }, SAVE_DELAY);
}

// Add event listeners to all form inputs for auto-save
function setupAutoSave() {
    // Get all form inputs
    const form = document.getElementById('config-form');
    const inputs = form.querySelectorAll('input, select');
    
    // Add change listener to each input
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            input.addEventListener('change', autoSaveConfig);
        } else if (input.type === 'number' || input.type === 'text') {
            input.addEventListener('input', autoSaveConfig);
        } else if (input.tagName === 'SELECT') {
            input.addEventListener('change', autoSaveConfig);
        }
    });
}

// Update the setup-venv handler
document.getElementById('setup-venv').addEventListener('click', async () => {
    const setupButton = document.getElementById('setup-venv');
    setupButton.disabled = true;
    setupButton.classList.add('opacity-50', 'cursor-not-allowed');
    
    try {
        await handleAsyncAction('Install requirements', async () => {
            return await window.electronAPI.installRequirements();
        });
        // Reload microphones after successful installation
        await loadMicrophones();
    } finally {
        setupButton.disabled = false;
        setupButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});

// Simplified microphone loading
async function loadMicrophones() {
    const microphoneSelect = document.getElementById('microphone');
    
    try {
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
        
        // Restore previously selected microphone if possible
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

// Update window load to include auto-save setup
window.addEventListener('load', async () => {
    appendToConsole('TaSTT Configuration UI initialized', 'info');
    
    // Load config first
    try {
        const config = await window.electronAPI.loadConfig();
        setFormValues(config);
        appendToConsole('Configuration loaded', 'info');
    } catch (error) {
        appendToConsole(`Failed to load configuration: ${error.message}`, 'stderr');
    }
    
    // Load microphones
    await loadMicrophones();
    
    // Set up auto-save after everything is loaded
    setupAutoSave();
});

// Console management
const consoleContent = document.getElementById('console-content');

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
    
    // Auto-scroll to bottom
    const pythonConsole = document.getElementById('python-console');
    pythonConsole.scrollTop = pythonConsole.scrollHeight;
}

// Clear console button
document.getElementById('clear-console').addEventListener('click', () => {
    consoleContent.innerHTML = '';
    appendToConsole('Console cleared', 'info');
});

// Listen for Python output
window.electronAPI.onPythonOutput((data) => {
    appendToConsole(data.message, data.type);
});

document.getElementById('start-process').addEventListener('click', async () => {
    setButtonState(startButton, true);
    
    try {
        await window.electronAPI.startProcess();
        setProcessRunningState();
        appendToConsole('Process started successfully', 'info');
    } catch (error) {
        appendToConsole(`Failed to start process: ${error.message}`, 'stderr');
        setButtonState(startButton, false);
    }
});

document.getElementById('stop-process').addEventListener('click', async () => {
    setButtonState(stopButton, true);
    
    try {
        const result = await window.electronAPI.stopProcess();
        appendToConsole('Process stop initiated', 'info');
    } catch (error) {
        appendToConsole(`Failed to stop process: ${error.message}`, 'stderr');
        setButtonState(stopButton, false);
    }
});

// Listen for process stopped event
window.electronAPI.onProcessStopped(() => {
    setProcessStoppedState();
}); 
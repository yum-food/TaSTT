const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const fs = require('node:fs').promises;
const yaml = require('js-yaml');
const { spawn } = require('child_process');

const APP_ROOT = path.join(__dirname, '..');
const CONFIG_PATH = path.join(APP_ROOT, 'config.yaml');

let mainWindow;
let runningProcess = null; // Track the running Python process

// Helper function to get the correct Python executable from venv
function getVenvPython() {
  const venvPath = path.join(APP_ROOT, 'venv');
  const pythonPath = path.join(venvPath, 'Scripts', 'python.exe');
  return pythonPath;
}

// Helper function to send Python output to renderer
function sendPythonOutput(message, type = 'stdout') {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('python-output', { message, type });
  }
}

// Helper function to execute Python commands using venv
function executePythonCommand(args, options = {}) {
  return new Promise((resolve, reject) => {
    const pythonPath = getVenvPython();
    const commandStr = `${path.basename(pythonPath)} ${args.join(' ')}`;
    sendPythonOutput(`> ${commandStr}`, 'info');
    
    // Add dll directory to PATH for Windows DLL loading
    const dllPath = path.join(APP_ROOT, 'dll');
    const env = { ...process.env };
    env.PATH = `${dllPath};${env.PATH}`;
    
    const spawnOptions = {
      ...options,
      env
    };
    
    const pythonProcess = spawn(pythonPath, args, spawnOptions);
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => {
      const text = data.toString();
      stdout += text;
      sendPythonOutput(text.trimEnd(), 'stdout');
    });
    
    pythonProcess.stderr.on('data', (data) => {
      const text = data.toString();
      stderr += text;
      sendPythonOutput(text.trimEnd(), 'stderr');
    });
    
    pythonProcess.on('error', (error) => {
      sendPythonOutput(`Failed to start Python process: ${error.message}`, 'stderr');
      reject({ error: error.message, stdout, stderr });
    });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        sendPythonOutput(`Process exited with code ${code}`, 'stderr');
        reject({ code, stdout, stderr });
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile('index.html');
}

// Default configuration based on user's current config.yaml
const DEFAULT_CONFIG = {
  compute_type: 'float16',
  enable_debug_mode: 0,
  enable_previews: 1,
  save_audio: 0,
  language: 'english',
  gpu_idx: 0,
  max_speech_duration_s: 10,
  min_silence_duration_ms: 250,
  microphone: 0,
  model: 'turbo',
  reset_after_silence_s: 15,
  transcription_loop_delay_ms: 100,
  use_cpu: 0,
  block_width: 2,
  num_blocks: 40,
  rows: 10,
  cols: 24
};

// IPC handlers
ipcMain.handle('load-config', async () => {
  try {
    const fileContent = await fs.readFile(CONFIG_PATH, 'utf8');
    return yaml.load(fileContent);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // Config file doesn't exist, create it with defaults
      console.log('Config file not found, creating with defaults...');
      try {
        const yamlContent = yaml.dump(DEFAULT_CONFIG, { lineWidth: -1 });
        await fs.writeFile(CONFIG_PATH, yamlContent, 'utf8');
        console.log('Created config.yaml with default values');
        return DEFAULT_CONFIG;
      } catch (writeError) {
        console.error('Error creating default config:', writeError);
        // Return defaults even if we can't write the file
        return DEFAULT_CONFIG;
      }
    }
    console.error('Error loading config:', error);
    throw error;
  }
});

ipcMain.handle('save-config', async (event, config) => {
  try {
    const yamlContent = yaml.dump(config, { lineWidth: -1 });
    await fs.writeFile(CONFIG_PATH, yamlContent, 'utf8');
    return { success: true };
  } catch (error) {
    console.error('Error saving config:', error);
    throw error;
  }
});

ipcMain.handle('restart-app', () => {
  app.relaunch();
  app.exit();
});

ipcMain.handle('install-requirements', async (event) => {
  const requirementsPath = path.join(APP_ROOT, 'app', 'requirements.txt');
  
  try {
    // Check if requirements.txt exists
    await fs.access(requirementsPath);
    
    const result = await executePythonCommand(['-m', 'pip', 'install', '-r', requirementsPath]);
    
    return { success: true, message: 'Requirements installed successfully' };
  } catch (error) {
    console.error('Error installing requirements:', error);
    if (error.code === 'ENOENT') {
      throw new Error('requirements.txt not found');
    }
    throw new Error(`Installation failed: ${error.stderr || error.error || 'Unknown error'}`);
  }
});

ipcMain.handle('get-microphones', async () => {
  const scriptPath = path.join(APP_ROOT, 'app', 'list_microphones.py');
  
  try {
    const result = await executePythonCommand([scriptPath]);
    const microphones = JSON.parse(result.stdout.trim());
    console.log('Successfully retrieved microphones:', microphones);
    return microphones;
  } catch (error) {
    console.error('Failed to get microphones:', error);
    throw new Error(`Failed to get microphones: ${error.stderr || error.error || 'Unknown error'}`);
  }
});

// Add handlers for starting and stopping the process
ipcMain.handle('start-process', async () => {
  if (runningProcess) {
    throw new Error('Process is already running');
  }

  const scriptPath = path.join(APP_ROOT, 'app', 'hi.py');
  const configPath = CONFIG_PATH;
  
  try {
    const pythonPath = getVenvPython();
    const args = [scriptPath, '--config', configPath];
    
    sendPythonOutput(`Starting process: ${path.basename(pythonPath)} ${args.join(' ')}`, 'info');
    
    // Add dll directory to PATH for Windows DLL loading
    const dllPath = path.join(APP_ROOT, 'dll');
    const env = { ...process.env };
    env.PATH = `${dllPath};${env.PATH}`;
    
    runningProcess = spawn(pythonPath, args, { env });
    
    runningProcess.stdout.on('data', (data) => {
      const text = data.toString();
      sendPythonOutput(text.trimEnd(), 'stdout');
    });
    
    runningProcess.stderr.on('data', (data) => {
      const text = data.toString();
      sendPythonOutput(text.trimEnd(), 'stderr');
    });
    
    runningProcess.on('error', (error) => {
      sendPythonOutput(`Process error: ${error.message}`, 'stderr');
      runningProcess = null;
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('process-stopped');
      }
    });
    
    runningProcess.on('close', (code) => {
      sendPythonOutput(`Process exited with code ${code}`, 'info');
      runningProcess = null;
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('process-stopped');
      }
    });
    
    return { success: true };
  } catch (error) {
    runningProcess = null;
    throw error;
  }
});

ipcMain.handle('stop-process', async () => {
  if (!runningProcess) {
    throw new Error('No process is running');
  }
  
  return new Promise((resolve, reject) => {
    let forcefullyKilled = false;
    
    // Set up a timeout to force kill after 10 seconds
    const killTimeout = setTimeout(() => {
      if (runningProcess) {
        sendPythonOutput('Process did not stop gracefully, forcing termination...', 'stderr');
        forcefullyKilled = true;
        runningProcess.kill();
      }
    }, 10000);
    
    // Listen for the process to exit
    runningProcess.once('exit', (code, signal) => {
      clearTimeout(killTimeout);
      runningProcess = null;
      
      if (forcefullyKilled) {
        sendPythonOutput('Process forcefully terminated', 'info');
      } else {
        sendPythonOutput('Process stopped gracefully', 'info');
      }
      
      resolve({ success: true, forcefullyKilled });
    });
    
    // Send termination signal
    sendPythonOutput('Stopping process gracefully...', 'info');
    runningProcess.kill();
  });
});

// Clean up on app quit
app.on('before-quit', () => {
  if (runningProcess) {
    runningProcess.kill();
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  app.quit();
});


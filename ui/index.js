const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const fs = require('node:fs').promises;
const yaml = require('js-yaml');
const { spawn } = require('child_process');

let mainWindow;

// Helper function to get the correct Python executable from venv
function getVenvPython() {
  const venvPath = path.join(__dirname, '..', 'venv');
  const isWindows = process.platform === 'win32';
  const pythonExecutable = isWindows ? 'python.exe' : 'python';
  const pythonPath = path.join(venvPath, isWindows ? 'Scripts' : 'bin', pythonExecutable);
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
    
    const pythonProcess = spawn(pythonPath, args, options);
    
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

// Path to config.yaml (one level up from ui directory)
const configPath = path.join(__dirname, '..', 'config.yaml');

// IPC handlers
ipcMain.handle('load-config', async () => {
  try {
    const fileContent = await fs.readFile(configPath, 'utf8');
    return yaml.load(fileContent);
  } catch (error) {
    console.error('Error loading config:', error);
    throw error;
  }
});

ipcMain.handle('save-config', async (event, config) => {
  try {
    const yamlContent = yaml.dump(config, { lineWidth: -1 });
    await fs.writeFile(configPath, yamlContent, 'utf8');
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
  const requirementsPath = path.join(__dirname, '..', 'app', 'requirements.txt');
  
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
  const pythonScript = `
import pyaudio
import json
import sys

try:
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    microphones = []
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            microphones.append({
                'index': i,
                'name': device_info.get('name'),
                'defaultSampleRate': device_info.get('defaultSampleRate')
            })

    print(json.dumps(microphones))
    p.terminate()
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
`;

  try {
    const result = await executePythonCommand(['-c', pythonScript]);
    const microphones = JSON.parse(result.stdout.trim());
    console.log('Successfully retrieved microphones:', microphones);
    return microphones;
  } catch (error) {
    console.error('Failed to get microphones:', error);
    throw new Error(`Failed to get microphones: ${error.stderr || error.error || 'Unknown error'}`);
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});


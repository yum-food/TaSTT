const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    loadConfig: () => ipcRenderer.invoke('load-config'),
    saveConfig: (config) => ipcRenderer.invoke('save-config', config),
    restartApp: () => ipcRenderer.invoke('restart-app'),
    getMicrophones: () => ipcRenderer.invoke('get-microphones'),
    installRequirements: () => ipcRenderer.invoke('install-requirements'),
    startProcess: () => ipcRenderer.invoke('start-process'),
    stopProcess: () => ipcRenderer.invoke('stop-process'),
    onPythonOutput: (callback) => ipcRenderer.on('python-output', (event, data) => callback(data)),
    onProcessStopped: (callback) => ipcRenderer.on('process-stopped', (event) => callback())
});

console.log('Preload script loaded.');


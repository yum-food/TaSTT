const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    loadConfig: () => ipcRenderer.invoke('load-config'),
    saveConfig: (config) => ipcRenderer.invoke('save-config', config),
    restartApp: () => ipcRenderer.invoke('restart-app'),
    getMicrophones: () => ipcRenderer.invoke('get-microphones'),
    installRequirements: () => ipcRenderer.invoke('install-requirements'),
    onPythonOutput: (callback) => ipcRenderer.on('python-output', (event, data) => callback(data))
});

console.log('Preload script loaded.');


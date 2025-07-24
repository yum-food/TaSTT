const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    loadConfig: () => ipcRenderer.invoke('load-config'),
    saveConfig: (config) => ipcRenderer.invoke('save-config', config),
    resetConfig: () => ipcRenderer.invoke('reset-config'),
    getMicrophones: () => ipcRenderer.invoke('get-microphones'),
    installRequirements: () => ipcRenderer.invoke('install-requirements'),
    deleteVenvIndicatorFile: () => ipcRenderer.invoke('deleteVenvIndicatorFile'),
    resetVenv: () => ipcRenderer.invoke('reset-venv'),
    startProcess: () => ipcRenderer.invoke('start-process'),
    stopProcess: () => ipcRenderer.invoke('stop-process'),
    getProcessState: () => ipcRenderer.invoke('get-process-state'),
    onPythonOutput: (callback) => ipcRenderer.on('python-output', (event, data) => callback(data)),
    onProcessStopped: (callback) => ipcRenderer.on('process-stopped', () => callback())
});


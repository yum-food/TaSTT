const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const projectRoot = path.join(__dirname, '..', '..');
const venvPath = path.join(projectRoot, 'venv_clean');
const dllPath = path.join(projectRoot, 'dll_empty');

console.log('Creating empty virtual environment and dll directory...');

// Create empty dll directory
if (!fs.existsSync(dllPath)) {
    fs.mkdirSync(dllPath, { recursive: true });
    console.log('Created empty dll directory');
}

try {
    console.log('Creating new venv...');
    execSync(`python -m venv "${venvPath}"`, { stdio: 'inherit' });
    console.log('Empty venv created successfully!');
} catch (error) {
    console.error('Failed to create venv:', error);
    process.exit(1);
}


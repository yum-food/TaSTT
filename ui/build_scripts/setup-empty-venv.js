const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const projectRoot = path.join(__dirname, '..', '..');
const venvPath = path.join(projectRoot, 'venv_clean');
const dllPath = path.join(projectRoot, 'dll_empty');

console.log('Creating empty virtual environment and dll directory...');

// Delete dll & venv if they already exist
if (fs.existsSync(dllPath)) {
    fs.rmSync(dllPath, { recursive: true, force: true });
    console.log('Deleted existing dll directory');
}
if (fs.existsSync(venvPath)) {
    fs.rmSync(venvPath, { recursive: true, force: true });
    console.log('Deleted existing venv directory');
}

// Create empty dll folder
fs.mkdirSync(dllPath, { recursive: true });
console.log('Created empty dll directory');

// Create hermitic python venv
try {
    console.log('Creating new venv...');
    execSync(`python -m venv "${venvPath}"`, { stdio: 'inherit' });
    console.log('Empty venv created successfully!');
} catch (error) {
    console.error('Failed to create venv:', error);
    process.exit(1);
}


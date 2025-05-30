# TaSTT UI

The TaSTT is built using electron and tailwind.css.

First, install nodejs. Open PowerShell as administrator:

```bash
# Delete any existing install.
$ choco uninstall nodejs -y
$ choco install nodejs-lts -y
```

Now open a non-admin PowerShell terminal:

```bash
# Check your node and npm versions.
$ node -v
v22.16.0
$ npm -v
10.9.2
# Set up directory
$ mkdir ui
cd ui
npm init -y
npm install --save-dev electron
# Get tailwind and deps
npm install --save-dev tailwindcss@3 postcss autoprefixer concurrently cross-env
npx tailwindcss init -p
# Install vue.js
npm install --save-dev vue@3 @vitejs/plugin-vue vite yaml
npm install --save-dev js-yaml
```

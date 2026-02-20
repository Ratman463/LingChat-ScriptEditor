# LingChat Script Editor - Build Guide

This document provides step-by-step instructions for building the LingChat Script Editor application.

## Prerequisites

- **Node.js** (v20.19.0 or higher, or v22.12.0+)
- **pnpm** (Package manager)
- **Python 3.13** (with pip)
- **PyInstaller** (for Python backend packaging)

## Project Structure

```
LingChat-ScriptEditor/
├── frontend/          # Vue.js + Electron frontend
├── backend/           # FastAPI Python backend
└── README_BUILD.md    # This file
```

## Build Instructions

### 1. Install Dependencies

#### Frontend Dependencies
```bash
cd frontend
pnpm install
```

#### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Build Backend (Python API Server)

The backend is a FastAPI application packaged with PyInstaller.

```bash
cd backend
pyinstaller --onefile --name "ScriptEditorAPI" run.py
```

**Output:** `backend/dist/ScriptEditorAPI.exe`

**Note:** Do NOT include the `--add-data "scripts;scripts"` flag. The scripts folder should be external so users can modify their data.

### 3. Build Frontend (Electron App)

The frontend is a Vue.js application packaged with Electron.

```bash
cd frontend
pnpm electron:build
```

This command runs:
1. `pnpm build:css` - Builds Tailwind CSS
2. `pnpm build` - Builds the Vue.js application
3. `electron-builder` - Packages everything into an Electron app

**Output:**
- `frontend/app-release/win-unpacked/` - Portable version
- `frontend/app-release/LingChat Script Editor Setup 0.0.0.exe` - Windows installer

### 4. Full Build (One Command)

From the project root, run both builds:

```bash
# Build backend
cd backend
pip install -r requirements.txt
pyinstaller --onefile --name "ScriptEditorAPI" run.py

# Build frontend
cd ../frontend
pnpm install
pnpm electron:build
```

## Output Structure

After building, the output structure will be:

```
frontend/app-release/
├── win-unpacked/                    # Portable version
│   ├── LingChat Script Editor.exe   # Main executable
│   └── resources/
│       ├── app.asar                 # Frontend code
│       ├── backend/
│       │   └── ScriptEditorAPI.exe  # Backend API server
│       └── scripts/                 # User data (modifiable)
│           └── (script folders...)
│
└── LingChat Script Editor Setup 0.0.0.exe  # Windows installer
```

## Development Mode

### Run Frontend Dev Server
```bash
cd frontend
pnpm dev
```

### Run Backend Dev Server
```bash
cd backend
python run.py
```

### Run Electron in Dev Mode
```bash
cd frontend
pnpm electron:dev
```

**Note:** In development mode, the backend must be started manually on `localhost:8000`.

## Configuration

### Tailwind CSS
Tailwind CSS is configured using the CLI approach:
- Input: `frontend/input.css`
- Output: `frontend/public/output.css`
- Sources: `frontend/src/**/*.vue`, `frontend/src/**/*.ts`

### Electron Builder
Configuration is in `frontend/package.json` under the `"build"` key:
- `extraResources` - Includes backend exe and scripts folder
- `nsis` - Windows installer settings

### PyInstaller
The backend uses PyInstaller with:
- `--onefile` - Single executable output
- `--name "ScriptEditorAPI"` - Output filename

## Troubleshooting

### Common Issues

1. **"Access denied" error during build**
   - Close any running instances of the application
   - Delete the `app-release` or `dist` folder manually and retry

2. **Tailwind CSS not working**
   - Run `pnpm build:css` before `pnpm build`
   - Check that `input.css` includes `@source` directives

3. **Backend can't find scripts folder**
   - Ensure scripts folder exists at `resources/scripts/`
   - Check console output for the path being used

4. **Port 8000 already in use**
   - Kill any existing process on port 8000
   - On Windows: `taskkill /F /IM ScriptEditorAPI.exe`

## Clean Build

To do a clean build from scratch:

```bash
# Clean backend
cd backend
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue

# Clean frontend
cd ../frontend
Remove-Item -Recurse -Force dist, app-release, public/output.css -ErrorAction SilentlyContinue

# Rebuild
cd ../backend
pyinstaller --onefile --name "ScriptEditorAPI" run.py

cd ../frontend
pnpm electron:build
```

## Version Update

To update the version number:
1. Edit `frontend/package.json` - change `"version": "0.0.0"`
2. The installer will be named accordingly

---

For more information, see the main [README.md](README.md).
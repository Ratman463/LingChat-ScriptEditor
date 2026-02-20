# LingChat Script Editor

A visual script editor for LingChat, an LLM (Large Language Model) based game. This application allows users to create and customize game scripts with an intuitive visual interface.

## Features

- **Visual Script Editor** - Drag-and-drop interface for creating game scripts
- **Chapter Flow Management** - Visualize and manage chapter connections
- **Event System** - Create and edit various event types (dialogue, choices, scenes, etc.)
- **Character Management** - Define characters with expressions and AI personalities
- **Asset Management** - Organize backgrounds, music, and sound effects
- **Live Preview** - See changes in real-time
- **Cross-Platform** - Available as a standalone desktop application

## Screenshots

![Home View](docs/home-view.png)
*Script selection and creation interface*

![Editor View](docs/editor-view.png)
*Visual chapter flow editor*

## Installation

### Download Release
Download the latest release from the [Releases](../../releases) page.

### Run the Application
1. Extract the downloaded archive (or install via the setup exe)
2. Run `LingChat Script Editor.exe`
3. The backend server will start automatically

## Development

### Prerequisites
- Node.js v20.19.0+ or v22.12.0+
- pnpm
- Python 3.13
- pip

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/LingChat-ScriptEditor.git
   cd LingChat-ScriptEditor
   ```

2. **Install dependencies**
   ```bash
   # Frontend
   cd frontend
   pnpm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Run in development mode**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python run.py
   
   # Terminal 2 - Frontend
   cd frontend
   pnpm electron:dev
   ```

### Building

See [README_BUILD.md](README_BUILD.md) for detailed build instructions.

```bash
# Build backend
cd backend
pyinstaller --onefile --name "ScriptEditorAPI" run.py

# Build frontend
cd ../frontend
pnpm electron:build
```

## Project Structure

```
LingChat-ScriptEditor/
├── frontend/                    # Vue.js + Electron frontend
│   ├── src/
│   │   ├── components/          # Vue components
│   │   │   ├── ChapterFlowCanvas.vue    # Main editor canvas
│   │   │   ├── ChapterNode.vue          # Chapter node component
│   │   │   └── EventCanvas.vue          # Event editing canvas
│   │   ├── views/               # Page views
│   │   │   ├── HomeView.vue     # Script selection
│   │   │   └── EditorView.vue   # Main editor
│   │   ├── stores/              # Pinia state management
│   │   └── config/              # Configuration files
│   ├── electron/                # Electron main process
│   └── public/                  # Static assets
│
├── backend/                     # FastAPI Python backend
│   ├── src/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   └── routers/             # API routes
│   │       ├── scripts.py       # Script management
│   │       ├── assets.py        # Asset management
│   │       └── characters.py    # Character management
│   ├── scripts/                 # Game scripts (user data)
│   └── run.py                   # Entry point
│
├── README.md                    # This file
└── README_BUILD.md              # Build instructions
```

## Script Format

Scripts are stored in YAML format with the following structure:

```
scripts/
└── my_script/
    ├── story_config.yaml        # Script metadata
    ├── Characters/              # Character definitions
    │   └── CharacterName/
    │       ├── settings.txt     # Character settings
    │       └── avatar/          # Expression images
    ├── Assests/                 # Assets
    │   ├── Backgrounds/
    │   ├── Musics/
    │   └── Sounds/
    └── Charpters/               # Chapter YAML files
        └── intro.yaml
```

### Example Chapter (YAML)

```yaml
events:
  - type: scene
    background: "school.png"
    music: "morning.mp3"
  
  - type: dialogue
    character: "Alice"
    expression: "happy"
    text: "Good morning!"
  
  - type: choice
    text: "How do you respond?"
    options:
      - text: "Say hello"
        next: "chapter2.yaml"
      - text: "Walk away"
        next: "chapter3.yaml"
  
  - type: end
    next: "chapter2.yaml"
```

## Supported Event Types

| Event Type | Description |
|------------|-------------|
| `scene` | Set background and music |
| `dialogue` | Character dialogue with expression |
| `choice` | Player choice with branching |
| `narration` | Narrative text |
| `condition` | Conditional branching |
| `ai_mode` | Enable AI-driven dialogue |
| `end` | Chapter end with next chapter link |

## Technology Stack

### Frontend
- **Vue.js 3** - UI framework
- **TypeScript** - Type safety
- **Pinia** - State management
- **Vue Router** - Navigation
- **Tailwind CSS** - Styling
- **Electron** - Desktop application framework

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **PyYAML** - YAML processing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Vue.js](https://vuejs.org/)
- Desktop framework by [Electron](https://www.electronjs.org/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/)

---

**LingChat Script Editor** - Create immersive LLM-powered game experiences
import os
import yaml
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict, Any
import sys

router = APIRouter(
    prefix="/api/preview",
    tags=["preview"]
)

if getattr(sys, 'frozen', False):
    exe_dir = Path(sys.executable).parent
    main_app_dir = exe_dir.parent.parent
    BASE_DIR = main_app_dir / "scripts"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"

def get_script_dir(script_id: str) -> Path:
    script_dir = BASE_DIR / script_id
    if not script_dir.exists():
        raise HTTPException(status_code=404, detail="Script not found")
    return script_dir

@router.get("/{script_id}/data")
async def get_preview_data(script_id: str):
    """Get all data needed for preview: config, chapters, and assets list"""
    script_dir = get_script_dir(script_id)
    
    # Load story config
    config_path = script_dir / "story_config.yaml"
    config = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    
    # Load all chapters
    chapters_dir = script_dir / "Chapters"
    chapters = {}
    if chapters_dir.exists():
        for root, dirs, files in os.walk(chapters_dir):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    full_path = Path(root) / file
                    rel_path = str(full_path.relative_to(chapters_dir)).replace("\\", "/")
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            chapters[rel_path] = yaml.safe_load(f) or {"events": []}
                    except Exception as e:
                        chapters[rel_path] = {"events": [], "error": str(e)}
    
    # Get assets (images, music, etc.) from both Assets and Characters folders
    assets = {}
    
    # Scan Assets folder if exists
    assets_dir = script_dir / "Assets"
    if assets_dir.exists():
        for root, dirs, files in os.walk(assets_dir):
            rel_root = Path(root).relative_to(assets_dir)
            for file in files:
                full_rel_path = str((rel_root / file).as_posix())
                assets[full_rel_path] = f"/api/preview/{script_id}/assets/{full_rel_path}"
    
    # Scan Characters folder for avatar images
    characters_dir = script_dir / "Characters"
    if characters_dir.exists():
        for char_folder in characters_dir.iterdir():
            if char_folder.is_dir():
                char_name = char_folder.name
                avatar_dir = char_folder / "avatar"
                if avatar_dir.exists():
                    for file in avatar_dir.iterdir():
                        if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                            # Store with multiple keys for easy lookup
                            emotion = file.stem  # filename without extension
                            key = f"Characters/{char_name}"
                            assets[key] = f"/api/preview/{script_id}/character/{char_name}"
                            assets[f"{char_name}"] = f"/api/preview/{script_id}/character/{char_name}"
                            assets[f"Characters/{char_name}/avatar/{emotion}"] = f"/api/preview/{script_id}/character/{char_name}/{emotion}"
    
    # Get character definitions
    characters = []
    if characters_dir.exists():
        for char_folder in characters_dir.iterdir():
            if char_folder.is_dir():
                char_name = char_folder.name
                # Check for settings.txt or any config file
                settings_file = char_folder / "settings.txt"
                character_info = {"id": char_name, "name": char_name}
                
                # Also add any avatar images info
                avatar_dir = char_folder / "avatar"
                if avatar_dir.exists():
                    emotions = [f.stem for f in avatar_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]
                    character_info["emotions"] = emotions
                
                characters.append(character_info)
    
    return {
        "config": config,
        "chapters": chapters,
        "assets": assets,
        "characters": characters
    }

@router.get("/{script_id}/assets/{asset_path:path}")
async def get_asset(script_id: str, asset_path: str):
    """Serve an asset file"""
    script_dir = get_script_dir(script_id)
    asset_file = script_dir / "Assets" / asset_path
    
    if asset_file.exists():
        return FileResponse(asset_file)
    
    # Try to find in subdirectories
    for root, dirs, files in os.walk(script_dir / "Assets"):
        for file in files:
            if file == asset_path or file.endswith(asset_path):
                return FileResponse(Path(root) / file)
    
    raise HTTPException(status_code=404, detail=f"Asset not found: {asset_path}")


@router.get("/{script_id}/character/{character_id}/{emotion}")
async def get_character_emotion_image(script_id: str, character_id: str, emotion: str = "正常"):
    """Serve a character emotion image"""
    script_dir = get_script_dir(script_id)
    
    # Try Characters/{character_id}/avatar/{emotion}.png
    avatar_path = script_dir / "Characters" / character_id / "avatar" / f"{emotion}.png"
    if avatar_path.exists():
        return FileResponse(avatar_path)
    
    # Try with .jpg extension
    avatar_path_jpg = script_dir / "Characters" / character_id / "avatar" / f"{emotion}.jpg"
    if avatar_path_jpg.exists():
        return FileResponse(avatar_path_jpg)
    
    # Fallback to "正常" or first available emotion
    avatar_dir = script_dir / "Characters" / character_id / "avatar"
    if avatar_dir.exists():
        # Try "正常" first as default
        normal_path = avatar_dir / "正常.png"
        if normal_path.exists():
            return FileResponse(normal_path)
        
        # Find first available image
        for file in avatar_dir.iterdir():
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                return FileResponse(file)
    
    raise HTTPException(status_code=404, detail=f"Character image not found: {character_id}/{emotion}")


@router.get("/{script_id}/character/{character_id}")
async def get_character_image(script_id: str, character_id: str):
    """Serve a character's default image"""
    script_dir = get_script_dir(script_id)
    
    # Try Characters/{character_id}/avatar/正常.png (or similar default)
    avatar_dir = script_dir / "Characters" / character_id / "avatar"
    
    if avatar_dir.exists():
        # Try common default emotions
        for default_name in ["正常", "默认", "default", "Default", "normal", "Normal"]:
            for ext in [".png", ".jpg", ".jpeg"]:
                default_path = avatar_dir / f"{default_name}{ext}"
                if default_path.exists():
                    return FileResponse(default_path)
        
        # Fallback to first available image
        for file in avatar_dir.iterdir():
            if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                return FileResponse(file)
    
    # Try other locations
    possible_paths = [
        script_dir / "Assets" / "Characters" / character_id,
        script_dir / "Assets" / "Characters" / f"{character_id}.png",
        script_dir / "Characters" / character_id / f"{character_id}.png",
    ]
    
    for path in possible_paths:
        if path.exists():
            return FileResponse(path)
    
    raise HTTPException(status_code=404, detail=f"Character image not found: {character_id}")

@router.get("/{script_id}", response_class=HTMLResponse)
async def get_preview_page(script_id: str):
    """Return the preview HTML page"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: #1a1a2e;
            color: white;
            overflow: hidden;
        }
        
        #game-container {
            width: 100vw;
            height: 100vh;
            position: relative;
            display: flex;
            flex-direction: column;
        }
        
        #background-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center;
            background-color: #16213e;
            z-index: 1;
        }
        
        #character-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 70%;
            display: flex;
            justify-content: center;
            align-items: flex-end;
            z-index: 2;
        }
        
        .character {
            max-height: 80%;
            max-width: 30%;
            object-fit: contain;
            margin: 0 2%;
        }
        
        #dialogue-box {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 80%, transparent 100%);
            padding: 20px 40px 30px;
            z-index: 10;
            min-height: 200px;
        }
        
        #speaker-name {
            font-size: 18px;
            font-weight: bold;
            color: #a855f7;
            margin-bottom: 10px;
            padding: 5px 15px;
            background: rgba(168, 85, 247, 0.2);
            border-radius: 5px;
            display: inline-block;
        }
        
        #dialogue-text {
            font-size: 16px;
            line-height: 1.6;
            min-height: 60px;
        }
        
        #choices-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 20;
        }
        
        .choice-button {
            padding: 15px 30px;
            background: rgba(168, 85, 247, 0.3);
            border: 2px solid #a855f7;
            color: white;
            font-size: 16px;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
            min-width: 300px;
        }
        
        .choice-button:hover {
            background: rgba(168, 85, 247, 0.6);
            transform: scale(1.05);
        }
        
        #click-indicator {
            position: absolute;
            bottom: 220px;
            right: 40px;
            color: rgba(255,255,255,0.5);
            font-size: 14px;
            animation: pulse 1.5s infinite;
            z-index: 15;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        #loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            z-index: 100;
        }
        
        .hidden {
            display: none !important;
        }
        
        #controls {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 100;
            display: flex;
            gap: 10px;
        }
        
        .control-btn {
            padding: 8px 16px;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            cursor: pointer;
            border-radius: 5px;
            font-size: 12px;
        }
        
        .control-btn:hover {
            background: rgba(0,0,0,0.7);
        }
        
        #error-display {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(239, 68, 68, 0.9);
            padding: 20px;
            border-radius: 10px;
            max-width: 80%;
            z-index: 200;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="loading">加载中...</div>
        <div id="background-layer"></div>
        <div id="character-layer"></div>
        <div id="dialogue-box">
            <div id="speaker-name"></div>
            <div id="dialogue-text"></div>
        </div>
        <div id="choices-container" class="hidden"></div>
        <div id="click-indicator">点击继续 ▼</div>
        <div id="controls">
            <button class="control-btn" onclick="restartGame()">重新开始</button>
            <button class="control-btn" onclick="toggleAuto()">自动播放</button>
        </div>
        <div id="error-display" class="hidden"></div>
    </div>
    
    <script>
        // Game State
        let gameState = {
            config: {},
            chapters: {},
            assets: {},
            characters: [],
            currentChapter: null,
            currentEventIndex: 0,
            currentBackground: null,
            currentCharacters: {},
            autoMode: false,
            autoInterval: null
        };
        
        // Load game data
        async function loadGameData() {
            const pathParts = window.location.pathname.split('/');
            const scriptId = pathParts[pathParts.length - 1];
            
            try {
                const response = await fetch(`/api/preview/${scriptId}/data`);
                const data = await response.json();
                
                gameState.config = data.config || {};
                gameState.chapters = data.chapters || {};
                gameState.assets = data.assets || {};
                gameState.characters = data.characters || [];
                
                // Start with intro chapter
                const introChapter = gameState.config.intro_chapter;
                if (introChapter && gameState.chapters[introChapter]) {
                    gameState.currentChapter = introChapter;
                } else {
                    // Use first available chapter
                    const chapterKeys = Object.keys(gameState.chapters);
                    if (chapterKeys.length > 0) {
                        gameState.currentChapter = chapterKeys[0];
                    }
                }
                
                document.getElementById('loading').classList.add('hidden');
                
                if (gameState.currentChapter) {
                    playEvent();
                } else {
                    showError('没有找到章节文件');
                }
            } catch (e) {
                showError('加载游戏数据失败: ' + e.message);
            }
        }
        
        function showError(message) {
            document.getElementById('loading').classList.add('hidden');
            const errorDisplay = document.getElementById('error-display');
            errorDisplay.textContent = message;
            errorDisplay.classList.remove('hidden');
        }
        
        function playEvent() {
            const chapter = gameState.chapters[gameState.currentChapter];
            if (!chapter || !chapter.events) {
                showError('章节没有事件');
                return;
            }
            
            const event = chapter.events[gameState.currentEventIndex];
            if (!event) {
                // End of chapter
                showEndOfChapter();
                return;
            }
            
            processEvent(event);
        }
        
        function processEvent(event) {
            const type = event.type;
            
            switch (type) {
                case 'narration':
                    showText('', event.text || '');
                    break;
                    
                case 'player':
                    showText('玩家', event.text || '');
                    break;
                    
                case 'dialogue':
                    const charName = findCharacterName(event.character);
                    showText(charName, event.text || '');
                    break;
                    
                case 'ai_dialogue':
                    const aiCharName = findCharacterName(event.character);
                    showText(aiCharName, '[AI] ' + (event.text || '等待AI生成...'));
                    break;
                    
                case 'background':
                    setBackground(event.imagePath);
                    advanceEvent(); // Background events should auto-advance
                    break;
                    
                case 'music':
                    playMusic(event.musicPath);
                    advanceEvent();
                    break;
                    
                case 'modify_character':
                    modifyCharacter(event);
                    advanceEvent();
                    break;
                    
                case 'set_variable':
                    advanceEvent();
                    break;
                    
                case 'end':
                    if (event.next) {
                        if (event.next === 'end') {
                            showEndOfChapter();
                        } else {
                            jumpToChapter(event.next);
                        }
                    } else {
                        showEndOfChapter();
                    }
                    break;
                    
                default:
                    advanceEvent();
            }
        }
        
        function showText(speaker, text) {
            document.getElementById('speaker-name').textContent = speaker;
            document.getElementById('speaker-name').style.display = speaker ? 'inline-block' : 'none';
            document.getElementById('dialogue-text').textContent = text;
            document.getElementById('click-indicator').classList.remove('hidden');
        }
        
        function setBackground(imagePath) {
            if (!imagePath) return;
            
            const assetUrl = gameState.assets[imagePath];
            if (assetUrl) {
                document.getElementById('background-layer').style.backgroundImage = `url(${assetUrl})`;
            } else {
                // Try direct path
                const pathParts = window.location.pathname.split('/');
                const scriptId = pathParts[pathParts.length - 1];
                document.getElementById('background-layer').style.backgroundImage = 
                    `url(/api/preview/${scriptId}/assets/${imagePath})`;
            }
        }
        
        function playMusic(musicPath) {
            // Music playback would require audio element
            // For now, just log it
            console.log('Playing music:', musicPath);
        }
        
        function modifyCharacter(event) {
            const action = event.action;
            const character = event.character;
            
            switch (action) {
                case 'show_character':
                    gameState.currentCharacters[character] = true;
                    updateCharacterDisplay();
                    break;
                case 'hide_character':
                    delete gameState.currentCharacters[character];
                    updateCharacterDisplay();
                    break;
            }
        }
        
        function updateCharacterDisplay() {
            const layer = document.getElementById('character-layer');
            layer.innerHTML = '';
            
            const pathParts = window.location.pathname.split('/');
            const scriptId = pathParts[pathParts.length - 1];
            
            Object.keys(gameState.currentCharacters).forEach(charId => {
                const img = document.createElement('img');
                img.className = 'character';
                img.alt = charId;
                
                // Find character name for display
                const charName = findCharacterName(charId);
                img.title = charName;
                
                // Try multiple sources for character image
                let imgSrc = null;
                
                // 1. Check if there's a direct asset match
                const possibleAssetKeys = [
                    `Characters/${charId}`,
                    `Characters/${charId}.png`,
                    `characters/${charId}`,
                    `figures/${charId}`,
                    `${charId}`,
                    `${charId}.png`
                ];
                
                for (const key of possibleAssetKeys) {
                    if (gameState.assets[key]) {
                        imgSrc = gameState.assets[key];
                        break;
                    }
                }
                
                // 2. Try the character endpoint
                if (!imgSrc) {
                    imgSrc = `/api/preview/${scriptId}/character/${encodeURIComponent(charId)}`;
                }
                
                img.src = imgSrc;
                
                // Handle image load error with placeholder
                img.onerror = function() {
                    this.style.width = '200px';
                    this.style.height = '350px';
                    this.style.background = 'linear-gradient(135deg, #374151 0%, #1f2937 100%)';
                    this.style.borderRadius = '10px';
                    this.style.display = 'flex';
                    this.style.alignItems = 'center';
                    this.style.justifyContent = 'center';
                    this.style.border = '2px solid #4b5563';
                    this.style.color = '#9ca3af';
                    this.style.fontSize = '14px';
                    this.style.textAlign = 'center';
                    this.style.padding = '10px';
                    this.outerHTML = `<div style="width:200px;height:350px;background:linear-gradient(135deg, #374151 0%, #1f2937 100%);border-radius:10px;display:flex;align-items:center;justify-content:center;border:2px solid #4b5563;color:#9ca3af;font-size:14px;text-align:center;padding:10px;">${charName}</div>`;
                };
                
                layer.appendChild(img);
            });
        }
        
        function findCharacterName(charId) {
            if (!charId) return '未知角色';
            const char = gameState.characters.find(c => c.id === charId || c.name === charId);
            return char ? (char.name || char.id) : charId;
        }
        
        function jumpToChapter(chapterPath) {
            if (gameState.chapters[chapterPath]) {
                gameState.currentChapter = chapterPath;
                gameState.currentEventIndex = 0;
                playEvent();
            } else {
                showError('章节不存在: ' + chapterPath);
            }
        }
        
        function advanceEvent() {
            gameState.currentEventIndex++;
            playEvent();
        }
        
        function showEndOfChapter() {
            document.getElementById('dialogue-text').textContent = '— 章节结束 —';
            document.getElementById('speaker-name').style.display = 'none';
            document.getElementById('click-indicator').classList.add('hidden');
        }
        
        function restartGame() {
            gameState.currentEventIndex = 0;
            gameState.currentCharacters = {};
            document.getElementById('character-layer').innerHTML = '';
            playEvent();
        }
        
        function toggleAuto() {
            gameState.autoMode = !gameState.autoMode;
            if (gameState.autoMode) {
                gameState.autoInterval = setInterval(() => {
                    advanceEvent();
                }, 3000);
            } else {
                clearInterval(gameState.autoInterval);
            }
        }
        
        // Click to advance
        document.getElementById('dialogue-box').addEventListener('click', () => {
            if (!gameState.autoMode) {
                advanceEvent();
            }
        });
        
        document.getElementById('background-layer').addEventListener('click', () => {
            if (!gameState.autoMode) {
                advanceEvent();
            }
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' || e.code === 'Enter') {
                advanceEvent();
            }
        });
        
        // Start
        loadGameData();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)
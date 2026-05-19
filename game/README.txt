================================================================
  MY WONDERFUL JOURNEY
  An Interactive Educational Picture-Book Game for Children
  ELEC7078A HCI Group Project — 2025/26 Semester 2
================================================================

OVERVIEW
--------
"My Wonderful Journey" is a Python GUI desktop application built
with the pygame library. Children (aged 6–12) follow a story
through 5 acts — home, supermarket, forest, and back — learning
17 English words through interactive spelling mini-games, voice
narration, and animated animal encounters.

Target users : Children aged 6–12 (especially those with ADHD) and their parents / teachers.

================================================================
REQUIREMENTS
================================================================

  Python version : Python 3.10 or above
                   (tested on Python 3.10 / 3.11 / 3.12 / 3.13)
                   Download: https://www.python.org/downloads/

  External library:
    pygame 2.5.2   (GUI framework — audio, graphics, events)
    Source  : https://www.pygame.org / https://pypi.org/project/pygame/
    Licence : LGPL v2.1

  No other third-party libraries are required.
  All other modules used (os, sys, random, math, datetime) are
  part of the Python standard library.

================================================================
HOW TO BUILD / RUN
================================================================

STEP 1 — Install Python 3.10+
  Download and install from https://www.python.org/downloads/
  Make sure to tick "Add Python to PATH" during installation.

STEP 2 — Install pygame
  Open a terminal (Command Prompt / PowerShell) and run:

      pip install pygame==2.5.2

  Or use the provided requirements file:

      pip install -r requirements.txt

STEP 3 — Sync game assets (run ONCE before first launch)
  From inside the  game/  folder, run:

      python setup_assets.py

  This copies image and audio files from the parent directories
  (场景图/ and 音频/) into game/assets/.

STEP 4 — Launch the game
  From inside the  game/  folder, run:

      python main.py

  The game launches in full-screen mode at 1280 × 720 (letterbox
  scaled to fit any monitor resolution).

----------------------------------------------------------------
SPECIAL EXECUTION SETTINGS
----------------------------------------------------------------
  • The game MUST be launched from inside the  game/  directory
    (or with  game/  as the working directory), because asset
    paths are resolved relative to  main.py 's location.

  • Audio device required: the game uses pygame.mixer for BGM,
    voice narration, and sound effects. Ensure speakers /
    headphones are connected and system volume is not muted.

  • Full-screen mode: the window opens full-screen automatically.
    Press  F11  to toggle between full-screen and windowed mode.

  • Administrator rights are NOT required.

----------------------------------------------------------------
CONTROLS
----------------------------------------------------------------
  Mouse click   : all in-game interactions (spelling, buttons)
  F11           : toggle full-screen / windowed
  F12           : save a screenshot (saved as
                  screenshot_YYYYMMDD_HHMMSS.png in game/)
  ESC           : quit the game

================================================================
DIRECTORY STRUCTURE
================================================================

  game/
  ├── main.py                 ← entry point (all scenes, game loop)
  ├── setup_assets.py         ← one-time asset sync script
  ├── scene_manager.py        ← scene state-machine (web version)
  ├── game_state.py           ← global game state (web version)
  ├── requirements.txt        ← pip dependency list
  ├── README.txt              ← this file
  │
  ├── scenes/                 ← modular scene files (web version)
  │   ├── scene_title.py
  │   ├── scene_living_room.py
  │   ├── scene_transit.py
  │   ├── scene_shopping_list.py
  │   ├── scene_supermarket.py
  │   ├── scene_handbook.py
  │   ├── scene_forest.py
  │   ├── scene_challenge.py
  │   └── scene_result.py
  │
  ├── components/             ← reusable UI widgets
  │   ├── spelling_panel.py   ← letter-tile spelling widget
  │   └── dialogue_box.py     ← NPC dialogue overlay
  │
  ├── utils/                  ← helpers
  │   ├── asset_loader.py     ← image / audio path resolver
  │   └── audio_manager.py    ← BGM / voice / SFX channels
  │
  └── assets/                 ← populated by setup_assets.py
      ├── images/             ← scene PNGs (copied from 场景图/)
      └── audio/              ← MP3 files  (copied from 音频/)

  ../场景图/                  ← source scene images (118 PNGs)
  ../音频/                    ← source audio files  (99 MP3s)

================================================================
THIRD-PARTY LIBRARY DECLARATION
(required by assignment — must be cited in final report)
================================================================

  Library  : pygame
  Version  : 2.5.2
  Purpose  : Cross-platform GUI, 2-D rendering, audio playback,
             keyboard/mouse event handling for the desktop
             application.
  Source   : https://www.pygame.org
             https://pypi.org/project/pygame/
  Licence  : GNU LGPL version 2.1

  All image and audio assets (PNGs and MP3s) were created by
  the project team or are royalty-free materials produced /
  recorded specifically for this project.

================================================================
KNOWN LIMITATIONS
================================================================
  • Windows 10 / 11 recommended. macOS and Linux should work
    but have not been formally tested.
  • Minimum display resolution: 1024 × 576 (1280 × 720 optimal).
  • The game does NOT have an in-game volume control; adjust
    system volume as needed.

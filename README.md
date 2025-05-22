# 🤖 Pokémon Blue AI Player

This project features an AI agent that automatically plays Pokémon Blue using the PyBoy emulator and Google's Gemini multimodal AI model. The AI analyzes the game screen and context to make decisions, simulating button presses to navigate and progress through the game.

## Project Structure

- `game/`: Contains the Game Boy ROM file (e.g., `pokemon_blue.gb`).
- `saves/`: Stores game save states.
- `utils/`: Auxiliary functions and AI agent logic, including:
  - `pyboy_capture.py`: Handles PyBoy emulator initialization, screen capture, and button mapping.
  - `gemini_agent.py`: Implements the Gemini AI model for decision-making.
  - `memory_buffer.py`: Manages the AI's contextual memory.

## Running the Project

### 1. Prerequisites

- Python 3.9+ (Python 3.9 is required due to `Optional[str]` syntax compatibility).
- A Google Cloud Project with the Gemini API enabled.
- A valid Google API Key.

### 2. Setup

a. Clone this repository (or create the project structure manually).  
b. Place your `pokemon_blue.gb` ROM file inside the `game/` directory.

### 3. Install Dependencies

Open your terminal in the project's root directory and create a virtual environment (recommended):

```bash
python -m venv venv
```

Activate the virtual environment:

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.\venv\Scripts\activate.bat
```

**On Linux/macOS:**
```bash
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Google API Key

Set your Google API Key as an environment variable named `GOOGLE_API_KEY`.

**On Windows (Command Prompt, temporary):**
```cmd
set GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

**On Windows (PowerShell, temporary):**
```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

**On Linux/macOS (temporary):**
```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

> For a permanent setup, refer to your operating system's documentation for setting environment variables.

### 5. Run the AI Player

Execute the main script from your project's root directory while your virtual environment is active:

```bash
python main.py
```

The PyBoy emulator window should appear, and the AI will begin playing Pokémon Blue automatically. Output logs will be displayed in your terminal.
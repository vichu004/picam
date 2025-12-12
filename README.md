# ClearTag Pi Scanner
A lightweight, AI-powered product compliance scanner designed for Raspberry Pi.

## Features
- **Lightweight**: Optimized for Raspberry Pi (3B+, 4, 5).
- **Fast**: Uses efficient OCR and logic-based extraction (simulating LLM behavior for speed).
- **Privacy-First**: Runs completely offline/locally.
- **Responsive UI**: Modern glassmorphism design.

## Prerequisites (Raspberry Pi)
1. **Update System**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```
2. **Install System Dependencies**:
   ```bash
   sudo apt-get install python3-pip tesseract-ocr libtesseract-dev
   ```

## Installation
1. **Clone/Copy the code** to your Pi.
2. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

## Running the App
1. Start the server:
   ```bash
   python3 main.py
   ```
2. Open your browser and go to:
   - `http://localhost:8000` (if on the Pi itself)
   - `http://<PI_IP_ADDRESS>:8000` (from another device)

## "LLM" vs Lightweight Mode
Currently, the system uses a **Hybrid Approach** (OCR + Smart Logic) to ensure it runs in milliseconds on a Pi. 
Running a full Generative LLM (like Llama-3) on a Pi can take 30s-2min per inference, which is often too slow for a scanner.

### To use a Real LLM:
1. Install llama-cpp: `pip install llama-cpp-python`
2. Download a GGUF model (e.g., Phi-3 Mini) to a `models/` folder.
3. Modify `main.py` to use `utils.llm_scanner`.


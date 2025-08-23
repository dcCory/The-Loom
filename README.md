# The Loom: Your Local AI-Assisted Writing Environment ✍️🤖

## Project Overview

**The Loom** is a local, privacy-focused, and open-source AI-assisted writing environment designed to help creative writers overcome writer's block, maintain narrative consistency, and manage complex story elements. It leverages powerful Large Language Models (LLMs) running directly on your machine, offering features like intelligent text generation, character tracking, plot point management, and creative suggestions, all within a clean, intuitive interface.

### Key Features:

* **Local-First & Privacy-Focused:** All AI processing and data storage happen on your local machine. No data is sent to external servers.
* **Dynamic Model Loading:** Load various AI models (Hugging Face Transformers, ExLlamaV2, llama.cpp GGUF) from local files or directly from Hugging Face Hub.
* **Configurable AI Parameters:** Fine-tune generation with adjustable `max_new_tokens`, `temperature`, `top_k`, `top_p`, and `max_context` settings.
* **Context-Aware Generation:** AI leverages detailed character profiles and plot points to generate more consistent and relevant text.
* **Writer's Block Buster Tools:** Get targeted AI suggestions for next scenes, character ideas, dialogue sparks, and setting details.
* **Comprehensive Project Management:** Create, load, save, and delete entire story projects, each with its own characters, plot points, and story text.
* **Intuitive User Interface:** A clean React frontend with collapsible side panels for settings and tools.
* **GPU Acceleration:** Supports NVIDIA (CUDA) and AMD (Vulkan via llama.cpp) GPUs for faster inference.

---

## Installation Guide 🛠️

To get The Loom up and running, you'll need to set up both the backend (Python) and frontend (Node.js/React).

### Prerequisites:

* **Git:** For cloning the repository.
* **Python 3.12:** The backend requires this specific Python version.
* **Node.js LTS & npm:** For the frontend.
* **GPU Drivers (Optional but Recommended):**
    * **NVIDIA GPU:** Ensure you have NVIDIA drivers and CUDA Toolkit installed.
    * **AMD GPU:** Ensure you have AMD drivers that support ROCm/HIP or Vulkan.
* **C/C++ Build Tools:** Essential for compiling native Python packages.

### Steps:

1.  **Clone the Repository:**

    ```
    git clone git@github.com:dcCory/The-Loom.git # Or use HTTPS: [https://github.com/dcCory/The-Loom.git](https://github.com/dcCory/The-Loom.
    cd The-Loom
    ```

2.  **Run the Automated Installation Script:**
    There are three included install scripts included, choose the one for your appropriate operating system.
        Windows: windows_install.bat
        MacOS: macOS_install.sh
        Linux: linux_install.sh
    Ensure that the install file has the correct permissions to execute the file as a program.

    **During the script, you will be prompted to choose your device type (CPU, NVIDIA GPU, or AMD GPU).** This choice determines which AI inference libraries are installed..

    * **For NVIDIA GPU (CUDA) users:** The script will attempt to set `CUDA_HOME` for `exllamav2` compilation. Ensure your CUDA Toolkit is installed in a standard location (e.g., `/usr/local/cuda`).
    * **For AMD GPU (Vulkan) users:** The script will compile `llama-cpp-python` with Vulkan support. Ensure you have the appropriate drivers drivers installed on your system.

---

## Running the Application ▶️

Once installed, you can start both the backend and frontend servers with one of the included start scripts:
    Windows: windows_start.bat
    MacOS: macOS_start.sh
    Linux: linux_start.sh

Just like with the installation scripts, ensure these files have the proper permissions to execute as a program. Once running the startup script, it will show you the url of the UI. This is set as "http://localhost:3000/" by default.

## Obtaining AI Models

You will need to download your own AI models in the correct format for the inference library of your choice. The program searches for models in 'The Loom'/backend/models, this is where you will need to place any models you download from sources like HuggingFace.
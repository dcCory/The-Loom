# The Loom: User Manual 📖

Welcome to **The Loom**, a simple personal AI-assisted writing environment! This is my capstone project for my final college class and I hope you can enjoy it!

---

## 1. Introduction

The Loom is a local, privacy-focused, and open-source application built to be your creative partner. It runs powerful AI models directly on your computer, ensuring your work remains private and under your control. Whether you're battling writer's block, needing fresh ideas, or striving for narrative consistency, The Loom is here to help.

---

## 2. Getting Started and Launching The Loom

Before launching The Loom, ensure you've successfully completed the install process laid out in the included `README.md` file.
Instructions on how to start the application are also included in the 'README.md', but you essentially just need to pick the startup scrip that corresponds to your operating system.

## 3. Main Writing Interface



The central area of The Loom is your primary workspace.

* **Large Text Area:** This is where your story unfolds. You can type, edit, and view the AI-generated text here. This entire text content is also what's sent to the AI as context for subsequent generations.
* **Generate Text Button:** Click this button to have the loaded AI model continue your story based on the current text in the main area.
* **Save Project Button:** Saves the entire active project (story text, characters, plot points) to your local disk.
* **Load Project Button:** Opens the "Manage Projects" modal, allowing you to create new projects or load existing ones.

---

## 4. Settings Panel (Left Collapsible Panel)

Click the `▶` or `▼` icon on the left panel to expand/collapse the **Settings**. This panel allows you to configure your AI models and generation parameters.

### 4.1 Model Loading



This section controls which AI model your application uses.

* **Inference Library:** Select the software library used to run the AI model.
    * **Transformers (Hugging Face):** A versatile library for many models that can load directly from Hugging Face Hub..
    * **ExLlamaV2:** (Only visible if installed and CUDA detected) Optimized for fast inference of EXL2 quantized models on NVIDIA GPUs.
    * **llama.cpp:** (Only visible if installed) Optimized for GGUF models on CPU, CUDA, and Vulkan-compatible GPUs.
* **Model Selection:**
    * **Dropdown:** This menu will list any **local model files** detected in your `backend/models/` directory that are compatible with your selected Inference Library.
    * **"Hugging Face ID (Online)" (for Transformers):** If "Transformers" is selected, this option appears. Choose it, then type a Hugging Face model ID (e.g., `gpt2`) into the text input box that appears below.
* **Device:** Choose where the model will run.
    * **CPU:** Uses your computer's main processor (slower for large models, but perfectly fine for smaller parameter models.).
    * **CUDA (NVIDIA GPU):** Uses NVIDIA GPUs.
    * **Vulkan (AMD/Intel/NVIDIA):** Uses GPUs compatible with the Vulkan API (primarily for `llama.cpp`).
    * *(Note: If "ExLlamaV2" is selected, "Device" will be forced to "CUDA").*
* **Model Type:**
    * **Primary (Story Generation):** The main model used for continuing your story.
    * **Auxiliary (Suggestions):** A separate model (often smaller and faster) used for the AI suggestion tools labeled "Writers Block Buster" on the right hand side.
* **Load Model Button:** Click to load the selected model into memory. You'll receive an alert indicating success or failure.
* **Unload All Models Button:** Click to free up memory by unloading both the primary and auxiliary AI models.

### 4.2 AI Generation Parameters



These sliders and input boxes control how the AI generates text.

* **Max New Tokens:** The maximum number of new tokens the AI will generate in a single turn.
* **Temperature:** Controls the randomness of the output.
    * **Lower (e.g., 0.1-0.5):** More deterministic, focused, and repetitive.
    * **Higher (e.g., 0.8-1.5):** More creative, diverse, and potentially nonsensical.
* **Top K:** Limits the AI's choice of the next token to the `K` most probable options. Lower `K` makes output more focused; higher `K` allows more diversity.
* **Top P:** Limits the AI's choice of the next token to a cumulative probability `P`. It selects the smallest set of tokens whose cumulative probability exceeds `P`. Lower `P` makes output more focused; higher `P` allows more diversity.
* **Max Context:** The maximum number of tokens (input + output) the AI model can "remember" and process. This will depend on your model of choice as some models have larger context windows than others (e.g., 128000). Setting this correctly is crucial to avoid "index out of range" errors for longer generations and stories.

---

## 5. Project Management

Click the **"Load Project"** button next to "Generate Text" to open the "Manage Projects" panel.

This panel allows you to organize your different writing endeavors.

* **Create New Project:**
    1.  Enter a **"New Project Title"** in the input field.
    2.  Click the **"Create"** button.
    3.  The new project will be created, automatically saved, and loaded into your workspace.
* **Load / Delete Projects:**
    * A list of all projects saved on your disk is displayed.
    * **Project Title:** The name you gave your project.
    * **Load Button:** Click to load that project's story text, characters, and plot points into your active workspace. The button wont do anything if the project is already loaded.
    * **Delete Button:** Click to permanently delete the project file from your disk. You cannot delete the currently loaded project.

---

## 6. Character Management (Right Collapsible Panel)

Click the `▶` or `▼` icon on the right panel to expand/collapse the **Characters** panel.



This panel helps you keep track of your story's cast and provides context to the AI.

* **My Characters List:** Displays all characters associated with the **active project**.
    * **Checkbox:** Check a character's box to include their description and traits in the AI's generation context.
    * **Edit Button:** Opens a modal to modify the character's details.
    * **Delete Button:** Deletes the character from the active project.
* **Add Character Button:** Opens a panel to **Add New Character**, showcasing each field for the character's info.

---

## 7. Plot Point Management (Right Collapsible Panel)

Click the `▶` or `▼` icon on the right panel to expand/collapse the **Plot Points** panel.



This panel helps you outline your story and provides structural context to the AI.

* **My Plot Points List:** Displays all plot points associated with the **active project**.
    * **Checkbox:** Check a plot point's box to include its description in the AI's generation context.
    * **Edit Button:** Opens a modal to modify the plot point's details.
    * **Delete Button:** Deletes the plot point from the active project.
* **Add Plot Points Button:** Opens a modal to **Add New Plot Point** Fill in the form fields (Title, Description are required) and click "Add".

---

## 8. Writer's Block Buster Tools (Right Collapsible Panel)

Click the `▶` or `▼` icon on the right panel to expand/collapse the **Writer's Block** panel.



This panel offers targeted AI suggestions to help you break through creative impasses.

* **Suggestion Buttons:**
    * **Next Scene Idea:** Get a concise idea for what could happen next in your story.
    * **Character Idea:** Suggests a new character or development for an existing one.
    * **Dialogue Sparker:** Provides insights to possible ways to continue or start new conversations between characters.
    * **Setting Detail:** Generates descriptive details to enrich your current setting.
* **AI Suggestion Display:** The AI's generated suggestion will appear in this text box, it is only visible after a suggestion is generated.

---

## 9. Basic Troubleshooting 🐛

* **"Could not connect to backend..."**: Ensure your backend server is running, this can be verified by navigating to (http://localhost:3000/)
* **Model Loading Errors**:
    * **`OSError: CUDA_HOME environment variable is not set`**: This means `exllamav2` is installed on a non-CUDA system. Ensure you used the correct `requirements.txt` (`requirements-rocm.txt` or `requirements-cpu.txt` should NOT include `exllamav2`).
    * **"index out of range" during generation**: This means the AI's context window is exceeded.
        * Ensure "Max Context" in the Settings panel is set appropriately for your model.
        * Ensure "Max New Tokens" is not excessively high.

---

## 10. Tips for Best AI Results ✨

* **Be Specific in Your Story Text:** The more context and detail you provide in the main text area, the better the AI can understand your intent.
* **Use Characters and Plot Points:** Always select relevant characters and plot points to guide the AI's generation towards your narrative goals.
* **Experiment with Parameters:** Adjust `Temperature`, `Top K`, and `Top P` to find the right balance of creativity and coherence for your style.
* **Iterate:** AI generation is often a collaborative process. Generate a small chunk, edit it, then generate more.
* **Load Larger Models:** For higher quality and longer outputs, use larger, more capable AI models (e.g., 7B+ parameters) if your hardware allows.

---

Thank you for using The Loom! Happy writing!
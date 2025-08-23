// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './index.css';
import CollapsiblePanel from './components/CollapsiblePanel.js';
import ManageModal from './components/ManageModal.js';
import * as api from './services/api.js';

function App() {
  const [storyText, setStoryText] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [characters, setCharacters] = useState([]);
  const [plotPoints, setPlotPoints] = useState([]);
  const [selectedCharacters, setSelectedCharacters] = useState([]);
  const [selectedPlotPoints, setSelectedPlotPoints] = useState([]);
  const [backendReady, setBackendReady] = useState(false);

  // Model Loading States
  const [modelId, setModelId] = useState('Hugging Face ID');
  const [modelDevice, setModelDevice] = useState('cpu');
  const [modelType, setModelType] = useState('primary');
  const [inferenceLibrary, setInferenceLibrary] = useState('transformers'); // Default inference library
  const [availableModels, setAvailableModels] = useState([]);
  const [exllamav2Available, setExllamav2Available] = useState(false);
  const [llamaCppAvailable, setLlamaCppAvailable] = useState(false);
  
  const [aiSuggestion, setAiSuggestion] = useState('');
  const [isSuggesting, setIsSuggesting] = useState(false);

  const [isCharacterModalOpen, setIsCharacterModalOpen] = useState(false);
  const [isPlotPointModalOpen, setIsPlotPointModalOpen] = useState(false);
  const [editingCharacter, setEditingCharacter] = useState(null);
  const [editingPlotPoint, setEditingPlotPoint] = useState(null);

  const [newCharName, setNewCharName] = useState('');
  const [newCharDesc, setNewCharDesc] = useState('');
  const [newCharTraits, setNewCharTraits] = useState('');
  const [newCharMotivations, setNewCharMotivations] = useState('');
  const [newCharAppearance, setNewCharAppearance] = useState('');
  const [newCharStatus, setNewCharStatus] = useState('Alive');

  const [newPpTitle, setNewPpTitle] = useState('');
  const [newPpDesc, setNewPpDesc] = useState('');
  const [newPpStatus, setNewPpStatus] = useState('Planned');
  const [newPpType, setNewPpType] = useState('Major Plot Beat');

  // State for AI Generation Parameters
  const [maxNewTokens, setMaxNewTokens] = useState(200);
  const [temperature, setTemperature] = useState(0.8);
  const [topK, setTopK] = useState(50);
  const [topP, setTopP] = useState(0.95);
  const [maxContext, setMaxContext] = useState(4096);

  // This dynamically filters device options based on selected inference library
  const getDeviceOptions = () => {
    if (inferenceLibrary === 'exllamav2') {
      return [{ value: 'cuda', label: 'CUDA (NVIDIA GPU)' }];
    }
    // For transformers or llama_cpp, all options are potentially available
    return [
      { value: 'cpu', label: 'CPU' },
      { value: 'cuda', label: 'CUDA (NVIDIA GPU)' },
      { value: 'vulkan', label: 'Vulkan (AMD/Intel/NVIDIA)' },
    ];
  };

  // This resets the device if incompatible library is selected
  useEffect(() => {
    if (inferenceLibrary === 'exllamav2' && modelDevice !== 'cuda') {
      setModelDevice('cuda');
    }
  }, [inferenceLibrary, modelDevice]);


  // --- Initial Backend Check & Data Load ---
  useEffect(() => {
    const checkBackendAndLoadData = async () => {
      try {
        await api.testBackend();
        setBackendReady(true);
        console.log("Backend is ready and connected!");

        const loadedText = await api.getMainStoryText();
        setStoryText(loadedText.text);

        const loadedCharacters = await api.getAllCharacters();
        setCharacters(loadedCharacters);

        const loadedPlotPoints = await api.getAllPlotPoints();
        setPlotPoints(loadedPlotPoints);

        const modelsResponse = await api.getAvailableModels();
        setAvailableModels(modelsResponse.models);
        setExllamav2Available(modelsResponse.exllamav2_available);
        setLlamaCppAvailable(modelsResponse.llama_cpp_available);
        console.log("Available local models:", modelsResponse.models);

      } catch (err) {
        setError("Could not connect to backend or load initial data. Please ensure the backend server is running.");
        console.error("Backend connection or initial data load error:", err);
      }
    };

    checkBackendAndLoadData();
  }, []);

  // --- Handlers for Main Functionality (Generate & Save) ---
  const handleGenerateClick = async () => {
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }
    // Now, the entire storyText is the prompt for continuation
    if (!storyText.trim()) {
      setError("Story text cannot be empty for generation! Please type something to start.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const generateRequest = {
        prompt: storyText,
        max_new_tokens: maxNewTokens,
        temperature: temperature,
        top_k: topK,
        top_p: topP,
        selected_character_ids: selectedCharacters,
        selected_plot_point_ids: selectedPlotPoints,
      };

      const response = await api.generateStoryText(generateRequest);
      const newText = response.generated_text;
      setStoryText(prevText => prevText + newText); // Append new text directly
      // Removed: setPrompt(''); // No longer needed
      
      await api.saveMainStoryText(storyText + newText); // Save the updated full text
      console.log("Story text auto-saved after generation.");

    } catch (err) {
      setError(`Error generating text: ${err.message || err}`);
      console.error("Generation error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveStory = async () => {
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await api.saveMainStoryText(storyText);
      console.log("Story saved successfully!");
    } catch (err) {
      setError(`Error saving story: ${err.message || err}`);
      console.error("Story save error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Character/Plot Point Selection Handlers ---
  const handleCharacterSelect = (charId) => {
    setSelectedCharacters(prev =>
      prev.includes(charId) ? prev.filter(id => id !== charId) : [...prev, charId]
    );
  };

  const handlePlotPointSelect = (ppId) => {
    setSelectedPlotPoints(prev =>
      prev.includes(ppId) ? prev.filter(id => id !== ppId) : [...prev, ppId]
    );
  };

  // --- Model Loading Handler ---
  const handleLoadModel = async () => {
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }
    if (!modelId.trim() || modelId === "Hugging Face ID") {
      setError("Please select a model from the dropdown.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData = {
        model_id: modelId,
        device: modelDevice,
        model_type: modelType,
        inference_library: inferenceLibrary,
        max_context: maxContext,
      };
      const response = await api.loadModel(requestData);
      console.log(response.message);
      alert(response.message);
    } catch (err) {
      setError(`Error loading model: ${err.message || err}`);
      console.error("Model load error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Model Unload Handler
  const handleUnloadModels = async () => {
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }
    if (window.confirm("Are you sure you want to unload all AI models? This will free up VRAM/RAM.")) {
        setIsLoading(true);
        setError(null);
        try {
            const response = await api.unloadModels();
            console.log(response.message);
            alert(response.message);
        } catch (err) {
            setError(`Error unloading models: ${err.message || err}`);
            console.error("Model unload error:", err);
        } finally {
            setIsLoading(false);
        }
    }
  };

  // --- Writer's Block Buster Handlers ---
  const handleSuggest = async (suggestionType, requestBody) => {
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }
    setIsSuggesting(true);
    setAiSuggestion('');
    setError(null);

    try {
      let response;
      const baseRequest = {
        current_story_context: storyText, // Send the entire storyText as context
        selected_character_ids: selectedCharacters,
        selected_plot_point_ids: selectedPlotPoints,
        ...requestBody
      };

      switch (suggestionType) {
        case 'nextScene':
          response = await api.suggestNextScene(baseRequest);
          break;
        case 'characterIdea':
          response = await api.suggestCharacterIdea(baseRequest);
          break;
        case 'dialogueSparker':
          response = await api.suggestDialogueSparker(baseRequest);
          break;
        case 'settingDetail':
          response = await api.suggestSettingDetail(baseRequest);
          break;
        default:
          throw new Error('Unknown suggestion type');
      }
      setAiSuggestion(response.suggestion);
    } catch (err) {
      setError(`Error getting suggestion: ${err.message || err}`);
      console.error("Suggestion error:", err);
    } finally {
      setIsSuggesting(false);
    }
  };

  // --- Character Management Handlers ---
  const handleAddCharacter = async () => {
    setError(null);
    try {
      const newCharData = {
        name: newCharName,
        description: newCharDesc,
        traits: newCharTraits || undefined,
        motivations: newCharMotivations || undefined,
        physical_appearance: newCharAppearance || undefined,
        status: newCharStatus,
      };
      const createdChar = await api.createCharacter(newCharData);
      setCharacters(prev => [...prev, createdChar]);
      // Clear form and close modal
      setNewCharName(''); setNewCharDesc(''); setNewCharTraits('');
      setNewCharMotivations(''); setNewCharAppearance(''); setNewCharStatus('Alive');
      setIsCharacterModalOpen(false);
    } catch (err) {
      setError(`Error adding character: ${err.message || err}`);
      console.error("Add character error:", err);
    }
  };

  const handleEditCharacter = (char) => {
    setEditingCharacter(char);
    setNewCharName(char.name);
    setNewCharDesc(char.description);
    setNewCharTraits(char.traits || '');
    setNewCharMotivations(char.motivations || '');
    setNewCharAppearance(char.physical_appearance || '');
    setNewCharStatus(char.status);
    setIsCharacterModalOpen(true);
  };

  const handleUpdateCharacter = async () => {
    setError(null);
    if (!editingCharacter) return;
    try {
      const updatedData = {
        name: newCharName,
        description: newCharDesc,
        traits: newCharTraits || undefined,
        motivations: newCharMotivations || undefined,
        physical_appearance: newCharAppearance || undefined,
        status: newCharStatus,
      };
      const updatedChar = await api.updateCharacter(editingCharacter.id, updatedData);
      setCharacters(prev => prev.map(char => char.id === updatedChar.id ? updatedChar : char));
      setEditingCharacter(null);
      setIsCharacterModalOpen(false);
    } catch (err) {
      setError(`Error updating character: ${err.message || err}`);
      console.error("Update character error:", err);
    }
  };

  const handleDeleteCharacter = async (charId) => {
    setError(null);
    if (window.confirm("Are you sure you want to delete this character?")) { // Use browser confirm for simplicity
      try {
        await api.deleteCharacter(charId);
        setCharacters(prev => prev.filter(char => char.id !== charId));
        setSelectedCharacters(prev => prev.filter(id => id !== charId)); // Deselect if deleted
      } catch (err) {
        setError(`Error deleting character: ${err.message || err}`);
        console.error("Delete character error:", err);
      }
    }
  };

  const handleCloseCharacterModal = () => {
    setIsCharacterModalOpen(false);
    setEditingCharacter(null); // Clear editing state
    // Clear form inputs
    setNewCharName(''); setNewCharDesc(''); setNewCharTraits('');
    setNewCharMotivations(''); setNewCharAppearance(''); setNewCharStatus('Alive');
  };

  // --- Plot Point Management Handlers ---
  const handleAddPlotPoint = async () => {
    setError(null);
    try {
      const newPpData = {
        title: newPpTitle,
        description: newPpDesc,
        status: newPpStatus,
        type: newPpType || undefined,
      };
      const createdPp = await api.createPlotPoint(newPpData);
      setPlotPoints(prev => [...prev, createdPp]);
      // Clear form and close modal
      setNewPpTitle(''); setNewPpDesc(''); setNewPpStatus('Planned'); setNewPpType('Major Plot Beat');
      setIsPlotPointModalOpen(false);
    } catch (err) {
      setError(`Error adding plot point: ${err.message || err}`);
      console.error("Add plot point error:", err);
    }
  };

  const handleEditPlotPoint = (pp) => {
    setEditingPlotPoint(pp);
    setNewPpTitle(pp.title);
    setNewPpDesc(pp.description);
    setNewPpStatus(pp.status);
    setNewPpType(pp.type || 'Major Plot Beat');
    setIsPlotPointModalOpen(true);
  };

  const handleUpdatePlotPoint = async () => {
    setError(null);
    if (!editingPlotPoint) return;
    try {
      const updatedData = {
        title: newPpTitle,
        description: newPpDesc,
        status: newPpStatus,
        type: newPpType || undefined,
      };
      const updatedPp = await api.updatePlotPoint(editingPlotPoint.id, updatedData);
      setPlotPoints(prev => prev.map(pp => pp.id === updatedPp.id ? updatedPp : pp));
      setEditingPlotPoint(null);
      setIsPlotPointModalOpen(false);
    } catch (err) {
      setError(`Error updating plot point: ${err.message || err}`);
      console.error("Update plot point error:", err);
    }
  };

  const handleDeletePlotPoint = async (ppId) => {
    setError(null);
    if (window.confirm("Are you sure you want to delete this plot point?")) {
      try {
        await api.deletePlotPoint(ppId);
        setPlotPoints(prev => prev.filter(pp => pp.id !== ppId));
        setSelectedPlotPoints(prev => prev.filter(id => id !== ppId)); // Deselect if deleted
      } catch (err) {
        setError(`Error deleting plot point: ${err.message || err}`);
        console.error("Delete plot point error:", err);
      }
    }
  };

  const handleClosePlotPointModal = () => {
    setIsPlotPointModalOpen(false);
    setEditingPlotPoint(null); // Clear editing state
    // Clear form inputs
    setNewPpTitle(''); setNewPpDesc(''); setNewPpStatus('Planned'); setNewPpType('Major Plot Beat');
  };


  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex p-4 font-inter">
      {/* Left Collapsible Panel: Settings */}
      <CollapsiblePanel title="Settings" position="left">
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-300">Model Loading</h4>
          {/* NEW: Inference Library Selection */}
          <div>
            <label htmlFor="inferenceLibrary" className="block text-sm font-medium text-gray-400">Inference Library</label>
            <select
              id="inferenceLibrary"
              className="w-full p-2 bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={inferenceLibrary}
              onChange={(e) => setInferenceLibrary(e.target.value)}
            >
              <option value="transformers">Transformers (Hugging Face)</option>
              {exllamav2Available && <option value="exllamav2">ExLlamaV2 (Quantized)</option>}
              {llamaCppAvailable && <option value="llama_cpp">llama.cpp (GGUF)</option>}
            </select>
          </div>

          {/* Model ID Dropdown (from detected files) */}
          <div>
            <label htmlFor="modelId" className="block text-sm font-medium text-gray-400">Model File / Hugging Face ID</label>
            <select
              id="modelId"
              className="w-full p-2 bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={modelId}
              onChange={(e) => setModelId(e.target.value)}
            >
              {/* Special option for Hugging Face IDs */}
              <option value="Hugging Face ID">Enter Hugging Face ID...</option>
              {availableModels
                .filter(model => model.compatible_libraries.includes(inferenceLibrary)) // Filter by selected library
                .map(model => (
                  <option key={model.path} value={model.path}>
                    {model.filename} ({model.size_mb}MB)
                  </option>
                ))}
            </select>
            {/* This ensures the text input for Hugging Face ID's only appears if selected from the dropdown menu */}
            {modelId === "Hugging Face ID" && inferenceLibrary === "transformers" && (
              <input
                type="text"
                className="w-full p-2 mt-2 bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., gpt2 or mistralai/Mistral-7B-Instruct-v0.2"
                value={modelId === "Hugging Face ID" ? "" : modelId}
                onChange={(e) => setModelId(e.target.value)}
              />
            )}
          </div>

          {/* Device Selection */}
          <div>
            <label htmlFor="modelDevice" className="block text-sm font-medium text-gray-400">Device</label>
            <select
              id="modelDevice"
              className="w-full p-2 bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={modelDevice}
              onChange={(e) => setModelDevice(e.target.value)}
              disabled={inferenceLibrary === 'exllamav2' && modelDevice !== 'cuda'} // Disable if ExLlamaV2 and not CUDA
            >
              {getDeviceOptions().map(option => (
                <option key={option.value} value={option.value} disabled={inferenceLibrary === 'exllamav2' && option.value !== 'cuda'}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="modelType" className="block text-sm font-medium text-gray-400">Model Type</label>
            <select
              id="modelType"
              className="w-full p-2 bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
            >
              <option value="primary">Primary (Story Generation)</option>
              <option value="auxiliary">Auxiliary (Suggestions)</option>
            </select>
          </div>
          <button
            onClick={handleLoadModel}
            disabled={isLoading || !backendReady}
            className={`w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? 'Loading...' : 'Load Model'}
          </button>
          <button
            onClick={handleUnloadModels}
            disabled={isLoading || !backendReady}
            className={`w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''} mt-2`}
          >
            Unload All Models
          </button>

          {/* AI Generation Parameters Section */}
          <h4 className="text-md font-medium text-gray-300 mt-6">AI Generation Parameters</h4>
          <div className="space-y-3">
            {/* Max New Tokens */}
            <div>
              <label htmlFor="maxTokens" className="block text-sm font-medium text-gray-400">Max New Tokens: {maxNewTokens}</label>
              <input
                type="range"
                id="maxTokens"
                min="10"
                max="1000"
                step="10"
                value={maxNewTokens}
                onChange={(e) => setMaxNewTokens(Number(e.target.value))}
                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <input
                type="number"
                min="10"
                max="1000"
                step="10"
                value={maxNewTokens}
                onChange={(e) => setMaxNewTokens(Number(e.target.value))}
                className="w-full p-1 mt-1 text-xs bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Temperature */}
            <div>
              <label htmlFor="temperature" className="block text-sm font-medium text-gray-400">Temperature: {temperature}</label>
              <input
                type="range"
                id="temperature"
                min="0.1"
                max="2.0"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <input
                type="number"
                min="0.1"
                max="2.0"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full p-1 mt-1 text-xs bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Top K */}
            <div>
              <label htmlFor="topK" className="block text-sm font-medium text-gray-400">Top K: {topK}</label>
              <input
                type="range"
                id="topK"
                min="1"
                max="200"
                step="1"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <input
                type="number"
                min="1"
                max="200"
                step="1"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full p-1 mt-1 text-xs bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Top P */}
            <div>
              <label htmlFor="topP" className="block text-sm font-medium text-gray-400">Top P: {topP}</label>
              <input
                type="range"
                id="topP"
                min="0.0"
                max="1.0"
                step="0.01"
                value={topP}
                onChange={(e) => setTopP(Number(e.target.value))}
                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <input
                type="number"
                min="0.0"
                max="1.0"
                step="0.01"
                value={topP}
                onChange={(e) => setTopP(Number(e.target.value))}
                className="w-full p-1 mt-1 text-xs bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            {/* Max Context */}
            <div>
              <label htmlFor="maxContext" className="block text-sm font-medium text-gray-400">Max Context: {maxContext}</label>
              <input
                type="range"
                id="maxContext"
                min="512"
                max="131072" // Max for Gemma 3 is 128k, so 131072 is a good upper bound
                step="512"
                value={maxContext}
                onChange={(e) => setMaxContext(Number(e.target.value))}
                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <input
                type="number"
                min="512"
                max="131072"
                step="512"
                value={maxContext}
                onChange={(e) => setMaxContext(Number(e.target.value))}
                className="w-full p-1 mt-1 text-xs bg-gray-700 text-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </CollapsiblePanel>

      {/* Central Writing Area */}
      <div className="flex-grow flex flex-col items-center justify-between p-4 bg-gray-800 rounded-lg shadow-xl border border-gray-700 mx-4">
        <h2 className="text-3xl font-bold text-blue-400 mb-6">The Loom</h2>
        {error && (
          <div className="bg-red-800 text-white p-3 rounded-md mb-4 w-full text-center">
            {error}
          </div>
        )}
        {!backendReady && (
          <div className="bg-yellow-800 text-white p-3 rounded-md mb-4 w-full text-center">
            Connecting to backend... Please ensure backend server is running.
          </div>
        )}
        <textarea
          className="w-full flex-grow p-4 bg-gray-700 text-gray-100 rounded-md shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="Start your story here..."
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
        ></textarea>
        {/* Removed: Prompt input field */}
        <div className="w-full mt-4 flex justify-center space-x-4"> {/* Centered buttons */}
          <button
            onClick={handleGenerateClick}
            disabled={isLoading || !backendReady}
            className={`
              bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-md transition duration-200
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isLoading ? 'Generating...' : 'Generate Text'}
          </button>
          <button
            onClick={handleSaveStory}
            disabled={isLoading || !backendReady}
            className={`
              bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-md transition duration-200
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            Save Story
          </button>
        </div>
      </div>

      {/* Right Stacked Collapsible Panels */}
      <div className="flex flex-col space-y-4 flex-shrink-0">
        {/* Writer's Block Buster Tools */}
        <CollapsiblePanel title="Writer's Block" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300">Suggestions</h4>
            <button
              onClick={() => handleSuggest('nextScene', {})}
              disabled={isSuggesting || !backendReady}
              className={`w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
                ${isSuggesting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSuggesting ? 'Thinking...' : 'Next Scene Idea'}
            </button>
            <button
              onClick={() => handleSuggest('characterIdea', {})}
              disabled={isSuggesting || !backendReady}
              className={`w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
                ${isSuggesting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSuggesting ? 'Thinking...' : 'Character Idea'}
            </button>
            <button
              onClick={() => handleSuggest('dialogueSparker', {})}
              disabled={isSuggesting || !backendReady}
              className={`w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
                ${isSuggesting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSuggesting ? 'Thinking...' : 'Dialogue Sparker'}
            </button>
            <button
              onClick={() => handleSuggest('settingDetail', {})}
              disabled={isSuggesting || !backendReady}
              className={`w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200
                ${isSuggesting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSuggesting ? 'Thinking...' : 'Setting Detail'}
            </button>
            {aiSuggestion && (
              <div className="bg-gray-700 p-3 rounded-md text-sm text-gray-200 mt-4 break-words">
                <p className="font-semibold text-blue-300 mb-1">AI Suggestion:</p>
                <p>{aiSuggestion}</p>
                <button
                  onClick={() => setStoryText(prev => prev + "\n\n" + aiSuggestion)}
                  className="mt-2 text-xs bg-blue-500 hover:bg-blue-600 px-2 py-1 rounded-md"
                >
                  Insert into Story
                </button>
              </div>
            )}
            {!aiSuggestion && !isSuggesting && (
              <p className="text-sm text-gray-400 mt-4">Suggestions will appear here.</p>
            )}
          </div>
        </CollapsiblePanel>

        {/* Character Tracker Panel */}
        <CollapsiblePanel title="Characters" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300 mb-2">My Characters</h4>
            {characters.length === 0 ? (
              <p className="text-sm text-gray-400">No characters yet. Click "Manage" to add.</p>
            ) : (
              <ul className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {characters.map(char => (
                  <li key={char.id} className="flex items-center justify-between bg-gray-700 p-2 rounded-md">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCharacters.includes(char.id)}
                        onChange={() => handleCharacterSelect(char.id)}
                        className="form-checkbox h-4 w-4 text-blue-600 rounded"
                      />
                      <span className="text-gray-200 text-sm font-medium">{char.name}</span>
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditCharacter(char)}
                        className="text-blue-400 hover:text-blue-200 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteCharacter(char.id)}
                        className="text-red-400 hover:text-red-200 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <button
              onClick={() => setIsCharacterModalOpen(true)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200"
            >
              Manage Characters
            </button>
          </div>
        </CollapsiblePanel>

        {/* Plot Point Tracker Panel */}
        <CollapsiblePanel title="Plot Points" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300 mb-2">My Plot Points</h4>
            {plotPoints.length === 0 ? (
              <p className="text-sm text-gray-400">No plot points yet. Click "Manage" to add.</p>
            ) : (
              <ul className="space-y-2 max-h-48 overflow-y-auto pr-2">
                {plotPoints.map(pp => (
                  <li key={pp.id} className="flex items-center justify-between bg-gray-700 p-2 rounded-md">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedPlotPoints.includes(pp.id)}
                        onChange={() => handlePlotPointSelect(pp.id)}
                        className="form-checkbox h-4 w-4 text-blue-600 rounded"
                      />
                      <span className="text-gray-200 text-sm font-medium">{pp.title}</span>
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditPlotPoint(pp)}
                        className="text-blue-400 hover:text-blue-200 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeletePlotPoint(pp.id)}
                        className="text-red-400 hover:text-red-200 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <button
              onClick={() => setIsPlotPointModalOpen(true)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200"
            >
              Manage Plot Points
            </button>
          </div>
        </CollapsiblePanel>
      </div>

      {/* Character Management Modal */}
      <ManageModal
        isOpen={isCharacterModalOpen}
        onClose={handleCloseCharacterModal}
        title={editingCharacter ? "Edit Character" : "Add New Character"}
      >
        <form onSubmit={(e) => { e.preventDefault(); editingCharacter ? handleUpdateCharacter() : handleAddCharacter(); }} className="space-y-4">
          <div>
            <label htmlFor="charName" className="block text-sm font-medium text-gray-400">Name</label>
            <input type="text" id="charName" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharName} onChange={(e) => setNewCharName(e.target.value)} required />
          </div>
          <div>
            <label htmlFor="charDesc" className="block text-sm font-medium text-gray-400">Description</label>
            <textarea id="charDesc" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharDesc} onChange={(e) => setNewCharDesc(e.target.value)} rows="3" required></textarea>
          </div>
          <div>
            <label htmlFor="charTraits" className="block text-sm font-medium text-gray-400">Traits (comma-separated)</label>
            <input type="text" id="charTraits" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharTraits} onChange={(e) => setNewCharTraits(e.target.value)} />
          </div>
          <div>
            <label htmlFor="charMotivations" className="block text-sm font-medium text-gray-400">Motivations</label>
            <input type="text" id="charMotivations" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharMotivations} onChange={(e) => setNewCharMotivations(e.target.value)} />
          </div>
          <div>
            <label htmlFor="charAppearance" className="block text-sm font-medium text-gray-400">Physical Appearance</label>
            <input type="text" id="charAppearance" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharAppearance} onChange={(e) => setNewCharAppearance(e.target.value)} />
          </div>
          <div>
            <label htmlFor="charStatus" className="block text-sm font-medium text-gray-400">Status</label>
            <select id="charStatus" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newCharStatus} onChange={(e) => setNewCharStatus(e.target.value)}>
              <option value="Alive">Alive</option>
              <option value="Deceased">Deceased</option>
              <option value="Missing">Missing</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <button type="button" onClick={handleCloseCharacterModal} className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-md">Cancel</button>
            <button type="submit" className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md">
              {editingCharacter ? "Update Character" : "Add Character"}
            </button>
          </div>
        </form>
      </ManageModal>

      {/* Plot Point Management Modal */}
      <ManageModal
        isOpen={isPlotPointModalOpen}
        onClose={handleClosePlotPointModal}
        title={editingPlotPoint ? "Edit Plot Point" : "Add New Plot Point"}
      >
        <form onSubmit={(e) => { e.preventDefault(); editingPlotPoint ? handleUpdatePlotPoint() : handleAddPlotPoint(); }} className="space-y-4">
          <div>
            <label htmlFor="ppTitle" className="block text-sm font-medium text-gray-400">Title</label>
            <input type="text" id="ppTitle" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newPpTitle} onChange={(e) => setNewPpTitle(e.target.value)} required />
          </div>
          <div>
            <label htmlFor="ppDesc" className="block text-sm font-medium text-gray-400">Description</label>
            <textarea id="ppDesc" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newPpDesc} onChange={(e) => setNewPpDesc(e.target.value)} rows="3" required></textarea>
          </div>
          <div>
            <label htmlFor="ppStatus" className="block text-sm font-medium text-gray-400">Status</label>
            <select id="ppStatus" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newPpStatus} onChange={(e) => setNewPpStatus(e.target.value)}>
              <option value="Planned">Planned</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
              <option value="Abandoned">Abandoned</option>
            </select>
          </div>
          <div>
            <label htmlFor="ppType" className="block text-sm font-medium text-gray-400">Type</label>
            <select id="ppType" className="w-full p-2 bg-gray-700 text-gray-100 rounded-md" value={newPpType} onChange={(e) => setNewPpType(e.target.value)}>
              <option value="Major Plot Beat">Major Plot Beat</option>
              <option value="Character Arc">Character Arc</option>
              <option value="Subplot">Subplot</option>
              <option value="Worldbuilding">Worldbuilding</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <button type="button" onClick={handleClosePlotPointModal} className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-md">Cancel</button>
            <button type="submit" className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md">
              {editingPlotPoint ? "Update Plot Point" : "Add Plot Point"}
            </button>
          </div>
        </form>
      </ManageModal>
    </div>
  );
}

export default App;
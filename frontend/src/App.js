// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import './index.css';
import CollapsiblePanel from './components/CollapsiblePanel.js';
import * as api from './services/api.js'; // FastAPI service

function App() {
  // State variables for managing application data and UI
  const [storyText, setStoryText] = useState('');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [characters, setCharacters] = useState([]); // Stores fetched character data
  const [plotPoints, setPlotPoints] = useState([]); // Stores fetched plot point data
  const [selectedCharacters, setSelectedCharacters] = useState([]); // IDs of characters selected for AI context
  const [selectedPlotPoints, setSelectedPlotPoints] = useState([]); // IDs of plot points selected for AI context
  const [backendReady, setBackendReady] = useState(false); // Tracks backend connection status

  // --- Initial Backend Connection Check & Data Loading ---

  useEffect(() => {
    const checkBackendAndLoadData = async () => {
      try {
        // Test connection to the backend's root endpoint
        await api.testBackend();
        setBackendReady(true);
        console.log("Backend is ready and connected!");

        // Load the main story text from the backend
        const loadedText = await api.getMainStoryText();
        setStoryText(loadedText.text);

        // Load all characters from the backend
        const loadedCharacters = await api.getAllCharacters();
        setCharacters(loadedCharacters);

        // Load all plot points from the backend
        const loadedPlotPoints = await api.getAllPlotPoints();
        setPlotPoints(loadedPlotPoints);

      } catch (err) {
        // Display an error if backend connection or data loading fails
        setError("Could not connect to backend or load initial data. Please ensure the backend server is running.");
        console.error("Backend connection or initial data load error:", err);
      }
    };

    checkBackendAndLoadData();
  }, []);

  // --- Handlers for Main Functionality (Generate & Save) ---

  const handleGenerateClick = async () => {
    // Prevent generation if backend is not ready or prompt is empty
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }
    if (!prompt.trim()) {
      setError("Prompt cannot be empty! Please type something.");
      return;
    }

    setIsLoading(true); // Set loading state
    setError(null);    // Clear previous errors

    try {
      // Prepare the request data for AI generation
      const generateRequest = {
        prompt: storyText + "\n\n" + prompt, // Send current story + new prompt as context
        max_new_tokens: 200,
        temperature: 0.8,
        top_k: 50,
        top_p: 0.95,
        selected_character_ids: selectedCharacters, // Pass selected character UUIDs
        selected_plot_point_ids: selectedPlotPoints, // Pass selected plot point UUIDs
      };

      // Call the backend API to generate text
      const response = await api.generateStoryText(generateRequest);
      const newText = response.generated_text;

      // Append the newly generated text to the current story and clear the prompt
      setStoryText(prevText => prevText + "\n\n" + newText);
      setPrompt('');
      
      // Auto-save the updated full story text to the backend after generation
      await api.saveMainStoryText(storyText + "\n\n" + newText);
      console.log("Story text auto-saved after generation.");

    } catch (err) {
      // Catch and display any errors during generation
      setError(`Error generating text: ${err.message || err}`);
      console.error("Text generation error:", err);
    } finally {
      setIsLoading(false); // Reset loading state
    }
  };

  const handleSaveStory = async () => {
    // Prevent saving if backend is not ready
    if (!backendReady) {
      setError("Backend not connected. Please start the backend server.");
      return;
    }

    setIsLoading(true); // Set loading state
    setError(null);    // Clear previous errors

    try {
      // Call the backend API to explicitly save the current story text
      await api.saveMainStoryText(storyText);
      console.log("Story saved successfully!");
    } catch (err) {
      // Catch and display any errors during saving
      setError(`Error saving story: ${err.message || err}`);
      console.error("Story save error:", err);
    } finally {
      setIsLoading(false); // Reset loading state
    }
  };

  // --- Character/Plot Point Selection Handlers (for UI interaction) ---
  // These functions manage which characters/plot points are currently selected
  // to be sent as context to the AI.

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

  // --- Render the Application UI ---
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex p-4 font-inter">
      {/* Left Collapsible Panel: Settings */}
      <CollapsiblePanel title="Settings" position="left">
        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-300">Model Loading</h4>
          {}
          <p className="text-sm text-gray-400">Model loading UI will go here.</p>
          <button
            onClick={() => alert('Model Load UI coming soon!')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200"
          >
            Load Model
          </button>
        </div>
      </CollapsiblePanel>

      {/* Central Writing Area */}
      <div className="flex-grow flex flex-col items-center justify-between p-4 bg-gray-800 rounded-lg shadow-xl border border-gray-700 mx-4">
        <h2 className="text-3xl font-bold text-blue-400 mb-6">The Loom</h2>
        {/* Error and Backend Connection Status Messages */}
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
        
        {/* Main Story Textarea */}
        <textarea
          className="w-full flex-grow p-4 bg-gray-700 text-gray-100 rounded-md shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          placeholder="Start your story here..."
          value={storyText}
          onChange={(e) => setStoryText(e.target.value)}
        ></textarea>
        
        {/* Prompt Input and Action Buttons */}
        <div className="w-full mt-4 flex flex-col md:flex-row items-center space-y-3 md:space-y-0 md:space-x-4">
          <input
            type="text"
            className="flex-grow p-3 bg-gray-700 text-gray-100 rounded-md shadow-inner focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your prompt for AI generation..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyPress={(e) => { // Allows generating on Enter key press
              if (e.key === 'Enter' && !isLoading) {
                handleGenerateClick();
              }
            }}
          />
          <button
            onClick={handleGenerateClick}
            disabled={isLoading || !backendReady} // Disable when loading or backend not ready
            className={`
              bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-md transition duration-200
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isLoading ? 'Generating...' : 'Generate Text'}
          </button>
          <button
            onClick={handleSaveStory}
            disabled={isLoading || !backendReady} // Disable when loading or backend not ready
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
        {/* Writer's Block Buster Tools Panel */}
        <CollapsiblePanel title="Writer's Block" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300">Suggestions</h4>
            {/* Placeholder buttons for various suggestions */}
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Next Scene Idea
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Character Idea
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Dialogue Sparker
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Setting Detail
            </button>
            {/* Area where AI suggestions will be displayed */}
            <p className="text-sm text-gray-400 mt-4">Suggestions will appear here.</p>
          </div>
        </CollapsiblePanel>

        {/* Character Tracker Panel */}
        <CollapsiblePanel title="Characters" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300 mb-2">My Characters</h4>
            {/* Display list of characters or a message if none exist */}
            {characters.length === 0 ? (
              <p className="text-sm text-gray-400">No characters yet. Create some via backend API.</p>
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
                    {/* Placeholder for future edit/delete buttons */}
                  </li>
                ))}
              </ul>
            )}
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Manage Characters
            </button>
          </div>
        </CollapsiblePanel>

        {/* Plot Point Tracker Panel */}
        <CollapsiblePanel title="Plot Points" position="right">
          <div className="space-y-3">
            <h4 className="text-md font-medium text-gray-300 mb-2">My Plot Points</h4>
            {/* Display list of plot points or a message if none exist */}
            {plotPoints.length === 0 ? (
              <p className="text-sm text-gray-400">No plot points yet. Create some via backend API.</p>
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
                    {/* Placeholder for future edit/delete buttons */}
                  </li>
                ))}
              </ul>
            )}
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-200">
              Manage Plot Points
            </button>
          </div>
        </CollapsiblePanel>
      </div>
    </div>
  );
}

export default App;


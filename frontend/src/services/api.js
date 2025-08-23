// frontend/src/services/api.js
const API_HOST_PORT = 'http://localhost:8000'; 
const API_PREFIX = '/api';

// --- Utility for Making API Calls ---
async function callApi(endpoint, method = 'GET', data = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  const config = {
    method: method,
    headers: headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_HOST_PORT}${API_PREFIX}${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API Error: ${response.status} ${response.statusText}`);
    }
    
    if (response.status === 204) {
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error calling ${method} ${API_PREFIX}${endpoint}:`, error);
    throw error;
  }
}

// --- Backend Health Check Endpoint ---
export const testBackend = async () => {
  return fetch(`${API_HOST_PORT}/`).then(res => { // Now uses API_HOST_PORT
    if (!res.ok) throw new Error('Backend root not reachable');
    return res.json();
  });
};

// --- Story Generation & Persistence Endpoints ---
export const generateStoryText = async (requestData) => {
  return callApi('/story/generate', 'POST', requestData);
};

export const getMainStoryText = async () => {
  return callApi('/story/main_text');
};

export const saveMainStoryText = async (text) => {
  return callApi('/story/main_text', 'PUT', { text });
};

// --- Character Management Endpoints ---
export const createCharacter = async (characterData) => {
  return callApi('/character/', 'POST', characterData);
};

export const getAllCharacters = async () => {
  return callApi('/character/');
};

export const getCharacterById = async (id) => {
  return callApi(`/character/${id}`);
};

export const updateCharacter = async (id, updateData) => {
  return callApi(`/character/${id}`, 'PUT', updateData);
};

export const deleteCharacter = async (id) => {
  return callApi(`/character/${id}`, 'DELETE');
};

// --- Plot Point Management Endpoints ---
export const createPlotPoint = async (plotPointData) => {
  return callApi('/plot/', 'POST', plotPointData);
};

export const getAllPlotPoints = async () => {
  return callApi('/plot/');
};

export const getPlotPointById = async (id) => {
  return callApi(`/plot/${id}`);
};

export const updatePlotPoint = async (id, updateData) => {
  return callApi(`/plot/${id}`, 'PUT', updateData);
};

export const deletePlotPoint = async (id) => {
  return callApi(`/plot/${id}`, 'DELETE');
};

// --- Writer's Block Buster Endpoints ---
export const suggestNextScene = async (requestData) => {
  return callApi('/writer-block/suggest-next-scene', 'POST', requestData);
};

export const suggestCharacterIdea = async (requestData) => {
  return callApi('/writer-block/suggest-character-idea', 'POST', requestData);
};

export const suggestDialogueSparker = async (requestData) => {
  return callApi('/writer-block/suggest-dialogue-sparker', 'POST', requestData);
};

export const suggestSettingDetail = async (requestData) => {
  return callApi('/writer-block/suggest-setting-detail', 'POST', requestData);
};

// --- Model Loading Endpoint ---
export const loadModel = async (requestData) => {
  return callApi('/story/load_model', 'POST', requestData);
};

// --- Model Unload Endpoint ---
export const unloadModels = async () => {
  return callApi('/story/unload_models', 'POST');
};

// --- Endpoint to get available local models ---
export const getAvailableModels = async () => {
  return callApi('/story/available_models');
};
// src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api'; // FastAPI backend URL

// --- Utility for API Calls ---
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
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API Error: ${response.status} ${response.statusText}`);
    }

    if (response.status === 204) {
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Error calling ${method} ${endpoint}:`, error);
    throw error;
  }
}

// --- Backend Health Check ---
export const testBackend = async () => {
  return callApi('/'); // Calls the root endpoint for a simple check
};

// --- Story Generation Endpoints ---
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

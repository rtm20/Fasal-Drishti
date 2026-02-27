import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export const analyzeImage = async (file, language = 'en') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);
  
  const response = await api.post('/api/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const analyzeBase64 = async (imageBase64, language = 'en') => {
  const response = await api.post('/api/analyze/base64', {
    image_base64: imageBase64,
    language,
  });
  return response.data;
};

export const getDiseases = async () => {
  const response = await api.get('/api/diseases');
  return response.data;
};

export const getDisease = async (key) => {
  const response = await api.get(`/api/diseases/${key}`);
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get('/api/dashboard/stats');
  return response.data;
};

export const getSupportedInfo = async () => {
  const response = await api.get('/api/dashboard/supported');
  return response.data;
};

export const getScanHistory = async () => {
  const response = await api.get('/api/scans');
  return response.data;
};

export const getWhatsAppStatus = async () => {
  const response = await api.get('/api/whatsapp/status');
  return response.data;
};

export const simulateWhatsApp = async (type, text = '') => {
  const response = await api.post('/api/whatsapp/simulate', { type, text });
  return response.data;
};

export default api;

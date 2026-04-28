import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
});

export const predictNetwork = async (features) => {
  try {
    const res = await api.post('/predict/network', { features });
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.message);
  }
};

export const predictAnomaly = async (features) => {
  try {
    const res = await api.post('/predict/anomaly', { features });
    return res.data;
  } catch (err) {
    throw new Error(err.response?.data?.detail || err.message);
  }
};

export const predictEmail = async (text) => {
  try {
    const res = await api.post('/predict/email', { text });
    return res.data;
  } catch (err) {
    throw new Error('AI Service unavailable');
  }
};

export const predictUrl = async (url) => {
  try {
    const res = await api.post('/predict/url', { url });
    return res.data;
  } catch (err) {
    throw new Error('AI Service unavailable');
  }
};

export const checkHealth = async () => {
  try {
    const res = await api.get('/health');
    return res.data;
  } catch (err) {
    throw new Error('Offline');
  }
};

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

export default api;

export const fetcher = (url) => api.get(url).then(res => res.data);

// Site settings
export const getSiteSettings = () => api.get('/settings/');
export const getStats = () => api.get('/stats/');
export const search = (q) => api.get(`/search/?q=${encodeURIComponent(q)}`);
export const getSkills = () => api.get('/skills/');
export const getExperiences = () => api.get('/experiences/');
export const getEducations = () => api.get('/educations/');

// Articles
export const getArticles = (params = {}) => api.get('/articles/', { params });
export const getArticle = (slug) => api.get(`/articles/${slug}/`);
export const getArticleCategories = () => api.get('/articles/categories/');
export const getFeaturedArticles = () => api.get('/articles/featured/');

// Projects
export const getProjects = (params = {}) => api.get('/projects/', { params });
export const getProject = (slug) => api.get(`/projects/${slug}/`);
export const getProjectCategories = () => api.get('/projects/categories/');

// Portfolio
export const getPortfolio = (params = {}) => api.get('/portfolio/', { params });
export const getPortfolioItem = (slug) => api.get(`/portfolio/${slug}/`);

// Tips
export const getTips = (params = {}) => api.get('/tips/', { params });
export const getTip = (slug) => api.get(`/tips/${slug}/`);

// Contact
export const sendContact = (data) => api.post('/contact/', data);

// Newsletter
export const subscribe = (data) => api.post('/newsletter/subscribe/', data);

// Comments
export const getComments = (contentType, objectId) => 
  api.get(`/comments/?content_type=${contentType}&object_id=${objectId}`);
export const postComment = (data) => api.post('/comments/', data);

// Reactions
export const getReactions = (contentType, objectId) => 
  api.get(`/reactions/?content_type=${contentType}&object_id=${objectId}`);
export const toggleReaction = (data) => api.post('/reactions/', data);

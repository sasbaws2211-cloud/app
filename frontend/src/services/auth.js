import { jwtDecode } from 'jwt-decode';

export const authService = {
  login: (token) => {
    localStorage.setItem('token', token);
  },
  
  logout: () => {
    localStorage.removeItem('token');
  },
  
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      const decoded = jwtDecode(token);
      return decoded.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  },
  
  getCurrentUserId: () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
      const decoded = jwtDecode(token);
      return decoded.sub;
    } catch {
      return null;
    }
  },
};
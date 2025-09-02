class AuthService {
  constructor() {
    this.apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    this.tokenKey = 'access_token';
    this.refreshTokenKey = 'refresh_token';
    this.userKey = 'user_profile';
  }

  async login(email, password) {
    const response = await fetch(`${this.apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    const data = await response.json();
    
    localStorage.setItem(this.tokenKey, data.access_token);
    localStorage.setItem(this.refreshTokenKey, data.refresh_token);
    
    await this.fetchProfile();
    
    return data;
  }

  async register(email, password, role = 'user') {
    const response = await fetch(`${this.apiUrl}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, role })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }

    return await response.json();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem(this.refreshTokenKey);
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.apiUrl}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      this.logout();
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    
    localStorage.setItem(this.tokenKey, data.access_token);
    localStorage.setItem(this.refreshTokenKey, data.refresh_token);
    
    return data;
  }

  async fetchProfile() {
    const token = localStorage.getItem(this.tokenKey);
    if (!token) {
      throw new Error('No access token available');
    }

    const response = await fetch(`${this.apiUrl}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        try {
          await this.refreshToken();
          return this.fetchProfile();
        } catch (error) {
          this.logout();
          throw new Error('Authentication failed');
        }
      }
      throw new Error('Failed to fetch profile');
    }

    const profile = await response.json();
    localStorage.setItem(this.userKey, JSON.stringify(profile));
    
    return profile;
  }

  async logout() {
    const token = localStorage.getItem(this.tokenKey);
    
    if (token) {
      try {
        await fetch(`${this.apiUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        });
      } catch (error) {
        console.warn('Logout request failed:', error);
      }
    }

    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  getUser() {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch (error) {
      return false;
    }
  }

  async makeAuthenticatedRequest(url, options = {}) {
    let token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token available');
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    };

    let response = await fetch(url, {
      ...options,
      headers
    });

    if (response.status === 401) {
      try {
        await this.refreshToken();
        token = this.getToken();
        headers['Authorization'] = `Bearer ${token}`;
        
        response = await fetch(url, {
          ...options,
          headers
        });
      } catch (error) {
        this.logout();
        throw new Error('Authentication failed');
      }
    }

    return response;
  }
}

class MockAuthService {
  constructor() {
    this.tokenKey = 'access_token';
    this.refreshTokenKey = 'refresh_token';
    this.userKey = 'user_profile';
    this.mockUser = {
      id: 1,
      email: 'demo@neov3.com',
      role: 'user',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    };
  }

  async login(email, password) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email === 'demo@neov3.com' && password === 'demo123') {
          const mockTokens = {
            access_token: this.generateMockToken(),
            refresh_token: this.generateMockToken('refresh')
          };
          
          localStorage.setItem(this.tokenKey, mockTokens.access_token);
          localStorage.setItem(this.refreshTokenKey, mockTokens.refresh_token);
          localStorage.setItem(this.userKey, JSON.stringify(this.mockUser));
          
          resolve(mockTokens);
        } else {
          reject(new Error('Invalid credentials. Use demo@neov3.com / demo123'));
        }
      }, 1000);
    });
  }

  async register(email, password, role = 'user') {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newUser = {
          ...this.mockUser,
          email,
          role
        };
        resolve(newUser);
      }, 1000);
    });
  }

  async refreshToken() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockTokens = {
          access_token: this.generateMockToken(),
          refresh_token: this.generateMockToken('refresh')
        };
        
        localStorage.setItem(this.tokenKey, mockTokens.access_token);
        localStorage.setItem(this.refreshTokenKey, mockTokens.refresh_token);
        
        resolve(mockTokens);
      }, 500);
    });
  }

  async fetchProfile() {
    return new Promise((resolve) => {
      setTimeout(() => {
        localStorage.setItem(this.userKey, JSON.stringify(this.mockUser));
        resolve(this.mockUser);
      }, 300);
    });
  }

  async logout() {
    return new Promise((resolve) => {
      setTimeout(() => {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.userKey);
        resolve();
      }, 200);
    });
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  getUser() {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  async makeAuthenticatedRequest(url, options = {}) {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token available');
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    };

    return fetch(url, {
      ...options,
      headers
    });
  }

  generateMockToken(type = 'access') {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({
      sub: this.mockUser.id,
      email: this.mockUser.email,
      role: this.mockUser.role,
      type,
      exp: Math.floor(Date.now() / 1000) + (type === 'refresh' ? 86400 : 3600),
      iat: Math.floor(Date.now() / 1000)
    }));
    const signature = btoa('mock-signature');
    
    return `${header}.${payload}.${signature}`;
  }
}

const useRealAuthService = process.env.REACT_APP_USE_REAL_AUTH_SERVICE === 'true';
export default useRealAuthService ? new AuthService() : new MockAuthService();

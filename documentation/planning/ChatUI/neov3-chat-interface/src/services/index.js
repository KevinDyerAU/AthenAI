import websocketService from './websocket';
import fileService from './fileService';
import authService from './authService';

class ServiceManager {
  constructor() {
    this.websocket = websocketService;
    this.fileService = fileService;
    this.authService = authService;
    this.isInitialized = false;
    this.connectionStatus = {
      websocket: false,
      authenticated: false
    };
    this.listeners = new Map();
  }

  async initialize() {
    if (this.isInitialized) {
      return;
    }

    try {
      if (this.authService.isAuthenticated()) {
        const token = this.authService.getToken();
        await this.connectWebSocket(token);
        await this.authService.fetchProfile();
        this.connectionStatus.authenticated = true;
      }

      this.setupEventListeners();
      this.isInitialized = true;
      this.emit('initialized', { status: this.connectionStatus });
    } catch (error) {
      console.error('Service initialization failed:', error);
      this.emit('error', { type: 'initialization', error });
    }
  }

  async login(email, password) {
    try {
      const tokens = await this.authService.login(email, password);
      await this.connectWebSocket(tokens.access_token);
      this.connectionStatus.authenticated = true;
      this.emit('authenticated', { user: this.authService.getUser() });
      return tokens;
    } catch (error) {
      this.emit('error', { type: 'authentication', error });
      throw error;
    }
  }

  async logout() {
    try {
      this.websocket.disconnect();
      await this.authService.logout();
      this.connectionStatus.websocket = false;
      this.connectionStatus.authenticated = false;
      this.emit('logout');
    } catch (error) {
      this.emit('error', { type: 'logout', error });
      throw error;
    }
  }

  async connectWebSocket(token) {
    try {
      this.websocket.connect(token);
      this.connectionStatus.websocket = true;
      this.emit('websocket_connected');
    } catch (error) {
      this.connectionStatus.websocket = false;
      this.emit('error', { type: 'websocket', error });
      throw error;
    }
  }

  setupEventListeners() {
    this.websocket.on('connection_status', (data) => {
      this.connectionStatus.websocket = data.connected;
      this.emit('connection_status_changed', this.connectionStatus);
    });

    this.websocket.on('error', (error) => {
      this.emit('error', { type: 'websocket', error });
    });

    this.websocket.on('authenticated', (data) => {
      this.emit('websocket_authenticated', data);
    });

    this.websocket.on('new_message', (message) => {
      this.emit('new_message', message);
    });

    this.websocket.on('message_history', (data) => {
      this.emit('message_history', data);
    });

    this.websocket.on('agent_update', (data) => {
      this.emit('agent_update', data);
    });

    this.websocket.on('room_joined', (data) => {
      this.emit('room_joined', data);
    });
  }

  getConnectionStatus() {
    return {
      ...this.connectionStatus,
      websocket_details: this.websocket.getConnectionStatus()
    };
  }

  getServices() {
    return {
      websocket: this.websocket,
      fileService: this.fileService,
      authService: this.authService
    };
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  async joinConversation(conversationId) {
    if (!this.connectionStatus.websocket) {
      throw new Error('WebSocket not connected');
    }
    
    this.websocket.joinRoom(conversationId);
  }

  async leaveConversation(conversationId) {
    if (this.connectionStatus.websocket) {
      this.websocket.leaveRoom(conversationId);
    }
  }

  async sendMessage(conversationId, message, role = 'user') {
    if (!this.connectionStatus.websocket) {
      throw new Error('WebSocket not connected');
    }
    
    this.websocket.sendMessage(conversationId, message, role);
  }

  async uploadFile(file, metadata = {}) {
    return await this.fileService.uploadFile(file, metadata);
  }

  async listFiles(limit = 50, offset = 0) {
    return await this.fileService.listFiles(limit, offset);
  }

  async searchFiles(query, limit = 10) {
    return await this.fileService.searchFiles(query, limit);
  }

  async deleteFile(fileId) {
    return await this.fileService.deleteFile(fileId);
  }

  async downloadFile(fileId, fileName) {
    return await this.fileService.downloadFile(fileId, fileName);
  }
}

const serviceManager = new ServiceManager();

export default serviceManager;
export { websocketService, fileService, authService };

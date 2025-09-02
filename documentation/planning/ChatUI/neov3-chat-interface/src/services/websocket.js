import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.connectionId = null;
    this.userId = null;
    this.currentRoom = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect(token = null) {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
    
    const socketOptions = {
      transports: ['websocket'],
      forceNew: true,
    };

    if (token) {
      socketOptions.auth = { token };
    }

    this.socket = io(apiUrl, socketOptions);

    this.socket.on('connect', () => {
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('connected', (data) => {
      this.connectionId = data.connection_id;
      this.userId = data.user_id;
      this.emit('authenticated', data);
    });

    this.socket.on('disconnect', () => {
      this.isConnected = false;
      this.emit('connection_status', { connected: false });
      this.handleReconnect();
    });

    this.socket.on('error', (error) => {
      this.emit('error', error);
    });

    this.socket.on('room:joined', (data) => {
      this.currentRoom = data.conversation_id;
      this.emit('room_joined', data);
    });

    this.socket.on('history', (data) => {
      this.emit('message_history', data);
    });

    this.socket.on('message:new', (message) => {
      this.emit('new_message', message);
    });

    this.socket.on('agent:update', (data) => {
      this.emit('agent_update', data);
    });

    this.socket.on('agent_run:update', (data) => {
      this.emit('agent_run_update', data);
    });

    return this.socket;
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        if (!this.isConnected) {
          this.connect();
        }
      }, delay);
    }
  }

  joinRoom(conversationId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('room:join', { conversation_id: conversationId });
    }
  }

  leaveRoom(conversationId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('room:leave', { conversation_id: conversationId });
      if (this.currentRoom === conversationId) {
        this.currentRoom = null;
      }
    }
  }

  sendMessage(conversationId, message, role = 'user') {
    if (this.socket && this.isConnected) {
      this.socket.emit('message:send', {
        conversation_id: conversationId,
        message,
        role
      });
    }
  }

  getHistory(conversationId, limit = 50) {
    if (this.socket && this.isConnected) {
      this.socket.emit('history:get', {
        conversation_id: conversationId,
        limit
      });
    }
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

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.connectionId = null;
      this.userId = null;
      this.currentRoom = null;
    }
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      connectionId: this.connectionId,
      userId: this.userId,
      currentRoom: this.currentRoom
    };
  }
}

class MockWebSocketService {
  constructor() {
    this.isConnected = false;
    this.connectionId = null;
    this.userId = 'mock-user-123';
    this.currentRoom = null;
    this.listeners = new Map();
    this.messages = [];
    this.agents = [
      { id: 'coordinator', status: 'active', name: 'Coordinator Agent' },
      { id: 'analyst', status: 'available', name: 'Analysis Agent' },
      { id: 'researcher', status: 'busy', name: 'Research Agent' },
      { id: 'writer', status: 'offline', name: 'Writing Agent' },
      { id: 'reviewer', status: 'available', name: 'Review Agent' }
    ];
  }

  connect(token = null) {
    setTimeout(() => {
      this.isConnected = true;
      this.connectionId = 'mock-connection-' + Date.now();
      this.emit('connection_status', { connected: true });
      this.emit('authenticated', {
        connection_id: this.connectionId,
        user_id: this.userId
      });
      this.startMockAgentUpdates();
    }, 500);
    return Promise.resolve();
  }

  startMockAgentUpdates() {
    setInterval(() => {
      if (this.isConnected && this.currentRoom) {
        const agent = this.agents[Math.floor(Math.random() * this.agents.length)];
        const statuses = ['active', 'available', 'busy', 'offline'];
        agent.status = statuses[Math.floor(Math.random() * statuses.length)];
        
        this.emit('agent_update', {
          conversation_id: this.currentRoom,
          agent_id: agent.id,
          status: agent.status,
          data: { progress: Math.random() }
        });
      }
    }, 5000);
  }

  joinRoom(conversationId) {
    setTimeout(() => {
      this.currentRoom = conversationId;
      this.emit('room_joined', { conversation_id: conversationId });
      
      const mockHistory = [
        {
          id: 'msg-1',
          conversation_id: conversationId,
          role: 'user',
          content: 'Hello, I need help with my project.',
          created_at: Date.now() - 60000,
          user_id: this.userId
        },
        {
          id: 'msg-2',
          conversation_id: conversationId,
          role: 'assistant',
          content: 'Hello! I\'d be happy to help you with your project. What specific assistance do you need?',
          created_at: Date.now() - 30000,
          agent: 'coordinator'
        }
      ];
      
      this.emit('message_history', {
        conversation_id: conversationId,
        messages: mockHistory
      });
    }, 200);
  }

  leaveRoom(conversationId) {
    if (this.currentRoom === conversationId) {
      this.currentRoom = null;
    }
  }

  sendMessage(conversationId, message, role = 'user') {
    const newMessage = {
      id: 'msg-' + Date.now(),
      conversation_id: conversationId,
      role,
      content: message,
      created_at: Date.now(),
      user_id: role === 'user' ? this.userId : null,
      agent: role === 'assistant' ? 'coordinator' : null
    };

    this.messages.push(newMessage);
    this.emit('new_message', newMessage);

    if (role === 'user') {
      setTimeout(() => {
        const responses = [
          'I understand your request. Let me process that for you.',
          'That\'s an interesting question. Let me analyze the available information.',
          'I can help you with that. Here\'s what I found...',
          'Based on your input, I recommend the following approach.',
          'Let me coordinate with the appropriate agents to handle your request.'
        ];
        
        const response = responses[Math.floor(Math.random() * responses.length)];
        this.sendMessage(conversationId, response, 'assistant');
      }, 1000 + Math.random() * 2000);
    }
  }

  getHistory(conversationId, limit = 50) {
    const history = this.messages
      .filter(msg => msg.conversation_id === conversationId)
      .slice(-limit);
    
    setTimeout(() => {
      this.emit('message_history', {
        conversation_id: conversationId,
        messages: history
      });
    }, 100);
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

  disconnect() {
    this.isConnected = false;
    this.connectionId = null;
    this.currentRoom = null;
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      connectionId: this.connectionId,
      userId: this.userId,
      currentRoom: this.currentRoom
    };
  }
}

const useRealWebSocket = import.meta.env.VITE_USE_REAL_WEBSOCKET === 'true';
export default useRealWebSocket ? new WebSocketService() : new MockWebSocketService();

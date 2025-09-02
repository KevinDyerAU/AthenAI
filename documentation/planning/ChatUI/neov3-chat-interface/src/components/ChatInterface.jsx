import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Paperclip, MoreVertical, User, Database, Download } from 'lucide-react';
import { Button } from './ui/button';
import AgentPanel from './AgentPanel';
import KnowledgePanel from './KnowledgePanel';
import MessageThread from './MessageThread';
import ConfirmationDialog from './ConfirmationDialog';
import FileUpload from './FileUpload';
import DownloadManager from './DownloadManager';
import serviceManager from '../services';
import '../App.css';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingAgent, setTypingAgent] = useState(null);
  const [showAgentPanel, setShowAgentPanel] = useState(false);
  const [showKnowledgePanel, setShowKnowledgePanel] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showDownloadManager, setShowDownloadManager] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState('coordinator');
  const [connectionStatus, setConnectionStatus] = useState({ websocket: false, authenticated: false });
  const [currentConversationId] = useState('default-conversation-' + Date.now());
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const [downloads, setDownloads] = useState([
    {
      id: 1,
      name: 'Analysis Report.pdf',
      size: 2048576,
      type: 'application/pdf',
      status: 'completed',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      source: 'Analysis Agent',
      url: 'https://api.neov3.com/downloads/analysis-report.pdf'
    },
    {
      id: 2,
      name: 'Research Summary.docx',
      size: 1024000,
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      status: 'downloading',
      progress: 65,
      createdAt: new Date(Date.now() - 1800000).toISOString(),
      source: 'Research Agent',
      url: 'https://api.neov3.com/downloads/research-summary.docx'
    },
    {
      id: 3,
      name: 'Data Visualization.png',
      size: 512000,
      type: 'image/png',
      status: 'queued',
      createdAt: new Date(Date.now() - 900000).toISOString(),
      source: 'Visualization Agent',
      url: 'https://api.neov3.com/downloads/data-viz.png'
    }
  ]);

  const [agents] = useState([
    {
      id: 'coordinator',
      name: 'Main Coordinator',
      status: 'active',
      description: 'Orchestrates tasks and coordinates between specialized agents',
      metrics: {
        tasksCompleted: 127,
        avgResponseTime: '1.2s',
        successRate: '98%'
      }
    },
    {
      id: 'analyst',
      name: 'Data Analyst',
      status: 'available',
      description: 'Specializes in data analysis, visualization, and insights',
      metrics: {
        tasksCompleted: 89,
        avgResponseTime: '2.1s',
        successRate: '96%'
      }
    },
    {
      id: 'researcher',
      name: 'Research Agent',
      status: 'busy',
      description: 'Conducts research, gathers information, and synthesizes findings',
      metrics: {
        tasksCompleted: 156,
        avgResponseTime: '3.4s',
        successRate: '94%'
      }
    },
    {
      id: 'writer',
      name: 'Content Writer',
      status: 'offline',
      description: 'Creates written content, documentation, and reports',
      metrics: {
        tasksCompleted: 73,
        avgResponseTime: '4.2s',
        successRate: '97%'
      }
    },
    {
      id: 'reviewer',
      name: 'Quality Reviewer',
      status: 'available',
      description: 'Reviews and validates outputs for quality and accuracy',
      metrics: {
        tasksCompleted: 91,
        avgResponseTime: '1.8s',
        successRate: '99%'
      }
    }
  ]);

  const [knowledgeItems] = useState([
    {
      id: 1,
      title: 'Project Requirements Document',
      type: 'document',
      category: 'Documents',
      size: 2048576,
      lastModified: '2024-01-15',
      relevance: 0.95,
      tags: ['requirements', 'project', 'specifications'],
      description: 'Comprehensive project requirements and specifications document outlining all functional and non-functional requirements.',
      source: 'upload',
      thumbnail: null
    },
    {
      id: 2,
      title: 'API Documentation',
      type: 'document',
      category: 'Documentation',
      size: 1024000,
      lastModified: '2024-01-14',
      relevance: 0.88,
      tags: ['api', 'documentation', 'endpoints'],
      description: 'Complete API documentation including endpoints, request/response formats, and authentication methods.',
      source: 'agent',
      thumbnail: null
    },
    {
      id: 3,
      title: 'Database Schema Design',
      type: 'document',
      category: 'Documents',
      size: 512000,
      lastModified: '2024-01-13',
      relevance: 0.82,
      tags: ['database', 'schema', 'design'],
      description: 'Database schema design document with entity relationships and data flow diagrams.',
      source: 'upload',
      thumbnail: null
    },
    {
      id: 4,
      title: 'User Interface Mockups',
      type: 'image',
      category: 'Design',
      size: 3072000,
      lastModified: '2024-01-12',
      relevance: 0.76,
      tags: ['ui', 'mockups', 'design'],
      description: 'High-fidelity user interface mockups and wireframes for the application.',
      source: 'upload',
      thumbnail: '/api/thumbnails/ui-mockups.jpg'
    },
    {
      id: 5,
      title: 'Meeting Notes - Sprint Planning',
      type: 'conversation',
      category: 'Conversations',
      size: 128000,
      lastModified: '2024-01-11',
      relevance: 0.71,
      tags: ['meeting', 'sprint', 'planning'],
      description: 'Sprint planning meeting notes with task assignments and timeline discussions.',
      source: 'agent',
      thumbnail: null
    }
  ]);

  useEffect(() => {
    initializeServices();
    return () => {
      serviceManager.leaveConversation(currentConversationId);
    };
  }, [currentConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeServices = async () => {
    try {
      await serviceManager.initialize();
      
      serviceManager.on('connection_status_changed', (status) => {
        setConnectionStatus(status);
      });

      serviceManager.on('new_message', (newMessage) => {
        setMessages(prev => [...prev, newMessage]);
        setIsTyping(false);
        setTypingAgent(null);
      });

      serviceManager.on('message_history', (data) => {
        setMessages(data.messages || []);
      });

      serviceManager.on('agent_update', (data) => {
        if (data.status === 'typing') {
          setIsTyping(true);
          setTypingAgent(data.agent_id);
        } else {
          setIsTyping(false);
          setTypingAgent(null);
        }
      });

      serviceManager.on('room_joined', () => {
        console.log('Joined conversation room');
      });

      if (serviceManager.getConnectionStatus().websocket) {
        await serviceManager.joinConversation(currentConversationId);
      }
    } catch (error) {
      console.error('Failed to initialize services:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (message.trim() && connectionStatus.websocket) {
      try {
        await serviceManager.sendMessage(currentConversationId, message.trim(), 'user');
        setMessage('');
        setIsTyping(true);
        setTypingAgent(selectedAgent);
      } catch (error) {
        console.error('Failed to send message:', error);
        const errorMessage = {
          id: Date.now(),
          role: 'system',
          content: 'Failed to send message. Please check your connection.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } else if (!connectionStatus.websocket) {
      const errorMessage = {
        id: Date.now(),
        role: 'system',
        content: 'WebSocket not connected. Please refresh the page.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMessageAction = (action, messageId) => {
    console.log(`Action ${action} on message ${messageId}`);
  };

  const handleAgentSelect = (agentId) => {
    setSelectedAgent(agentId);
  };

  const handleKnowledgeSelect = (item) => {
    console.log('Knowledge item selected:', item);
  };

  const handleDeleteKnowledge = (itemId) => {
    console.log('Delete knowledge item:', itemId);
  };

  const handleFileUpload = async (fileData) => {
    try {
      const result = await serviceManager.uploadFile(fileData.file, {
        category: fileData.category || 'document',
        tags: fileData.tags || [],
        description: fileData.description || ''
      });
      
      const uploadMessage = {
        id: Date.now(),
        role: 'system',
        content: `File "${fileData.file.name}" uploaded successfully and queued for processing.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, uploadMessage]);
      setShowFileUpload(false);
    } catch (error) {
      console.error('File upload failed:', error);
      const errorMessage = {
        id: Date.now(),
        role: 'system',
        content: `Failed to upload file: ${error.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleDownload = (item) => {
    console.log('Download item:', item);
  };

  const handleDownloadDelete = (downloadId) => {
    console.log('Delete download:', downloadId);
  };

  const handleDownloadPreview = (downloadId) => {
    console.log('Preview download:', downloadId);
  };

  return (
    <div className="h-screen flex bg-background">
      {showAgentPanel && (
        <div className="w-80 border-r border-border">
          <AgentPanel 
            agents={agents}
            onAgentSelect={handleAgentSelect}
            onClose={() => setShowAgentPanel(false)}
          />
        </div>
      )}

      <div className="flex-1 flex flex-col">
        <div className="flex items-center gap-2 px-4 py-2 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${connectionStatus.websocket ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium text-foreground">NeoV3 Enhanced AI Agent OS</span>
            <span className="text-xs text-muted-foreground">
              {connectionStatus.websocket ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="flex-1"></div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAgentPanel(!showAgentPanel)}
              className="text-muted-foreground hover:text-foreground"
            >
              <User className="w-4 h-4" />
              <span className="ml-1 text-xs">Agents</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowKnowledgePanel(!showKnowledgePanel)}
              className="text-muted-foreground hover:text-foreground"
            >
              <Database className="w-4 h-4" />
              <span className="ml-1 text-xs">Knowledge</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDownloadManager(!showDownloadManager)}
              className="text-muted-foreground hover:text-foreground"
            >
              <Download className="w-4 h-4" />
              <span className="ml-1 text-xs">Downloads</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-muted-foreground hover:text-foreground"
            >
              <MoreVertical className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <MessageThread 
            messages={messages}
            isTyping={isTyping}
            typingAgent={typingAgent}
            onMessageAction={handleMessageAction}
          />
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-border p-4">
          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 resize-none bg-transparent border-0 focus:outline-none focus:ring-0 placeholder:text-muted-foreground text-sm py-3 px-4 max-h-32"
                rows={1}
              />
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFileUpload(true)}
                className="text-muted-foreground hover:text-foreground"
              >
                <Paperclip className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-muted-foreground hover:text-foreground"
              >
                <Mic className="w-4 h-4" />
              </Button>
              <Button
                onClick={handleSendMessage}
                disabled={!message.trim()}
                size="sm"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {showKnowledgePanel && (
        <div className="w-80 border-l border-border">
          <KnowledgePanel 
            items={knowledgeItems}
            onItemSelect={handleKnowledgeSelect}
            onItemDelete={handleDeleteKnowledge}
            onClose={() => setShowKnowledgePanel(false)}
            onUpload={() => setShowFileUpload(true)}
            onDownload={() => setShowDownloadManager(true)}
          />
        </div>
      )}

      {showFileUpload && (
        <FileUpload
          onFileUpload={handleFileUpload}
          onClose={() => setShowFileUpload(false)}
          maxFiles={5}
          maxSize={10 * 1024 * 1024}
        />
      )}

      {showDownloadManager && (
        <DownloadManager
          downloads={downloads}
          onClose={() => setShowDownloadManager(false)}
          onDownload={handleDownload}
          onDelete={handleDownloadDelete}
          onPreview={handleDownloadPreview}
        />
      )}

      {showConfirmDialog && (
        <ConfirmationDialog
          {...confirmAction}
          onClose={() => setShowConfirmDialog(false)}
        />
      )}
    </div>
  );
};

export default ChatInterface;

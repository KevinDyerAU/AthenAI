import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Paperclip, MoreVertical, ThumbsUp, ThumbsDown, RotateCcw, Edit3, Upload, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AgentPanel from './AgentPanel';
import KnowledgePanel from './KnowledgePanel';
import MessageThread from './MessageThread';
import ConfirmationDialog from './ConfirmationDialog';
import FileUpload from './FileUpload';
import DownloadManager from './DownloadManager';
import '../App.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'agent',
      agent: 'Main Coordinator',
      content: 'Hello! I\'m your Main Coordinator. I can help you with various tasks and coordinate with specialized agents when needed. How can I assist you today?',
      timestamp: new Date(Date.now() - 60000).toISOString(),
      actions: ['thumbs-up', 'thumbs-down']
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingAgent, setTypingAgent] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [knowledgePanelOpen, setKnowledgePanelOpen] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showDownloadManager, setShowDownloadManager] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
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
      source: 'Research Agent'
    },
    {
      id: 3,
      name: 'Data Visualization.png',
      size: 512000,
      type: 'image/png',
      status: 'failed',
      error: 'Network timeout',
      createdAt: new Date(Date.now() - 900000).toISOString(),
      source: 'Creative Agent'
    }
  ]);
  
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sample agents data
  const [agents] = useState([
    {
      id: 'coordinator',
      name: 'Main Coordinator',
      status: 'active',
      specialization: 'General coordination and task delegation',
      avatar: '🎯',
      responseTime: '< 1s',
      successRate: 98
    },
    {
      id: 'research',
      name: 'Research Agent',
      status: 'available',
      specialization: 'Information gathering and analysis',
      avatar: '🔍',
      responseTime: '2-5s',
      successRate: 95
    },
    {
      id: 'analysis',
      name: 'Analysis Agent',
      status: 'busy',
      specialization: 'Data analysis and insights',
      avatar: '📊',
      responseTime: '5-10s',
      successRate: 97
    },
    {
      id: 'creative',
      name: 'Creative Agent',
      status: 'available',
      specialization: 'Content creation and ideation',
      avatar: '🎨',
      responseTime: '3-8s',
      successRate: 92
    },
    {
      id: 'technical',
      name: 'Technical Agent',
      status: 'offline',
      specialization: 'Code and technical solutions',
      avatar: '⚙️',
      responseTime: '1-3s',
      successRate: 99
    }
  ]);

  // Sample knowledge items including uploads and generated content
  const [knowledgeItems] = useState([
    {
      id: 1,
      title: 'Q3 Sales Analysis',
      type: 'document',
      lastModified: '2 hours ago',
      relevance: 0.95,
      category: 'Documents',
      size: 2048576,
      source: 'upload',
      tags: ['sales', 'analysis', 'Q3'],
      description: 'Comprehensive analysis of Q3 sales performance across all regions'
    },
    {
      id: 2,
      title: 'Customer Feedback Summary',
      type: 'insight',
      lastModified: '1 day ago',
      relevance: 0.87,
      category: 'Insights',
      source: 'agent',
      tags: ['feedback', 'customers', 'insights'],
      description: 'AI-generated summary of customer feedback patterns and trends'
    },
    {
      id: 3,
      title: 'Project Roadmap 2025',
      type: 'document',
      lastModified: '3 days ago',
      relevance: 0.78,
      category: 'Documents',
      size: 1024000,
      source: 'upload',
      tags: ['roadmap', '2025', 'planning'],
      description: 'Strategic roadmap for 2025 initiatives and milestones'
    },
    {
      id: 4,
      title: 'Team Performance Metrics',
      type: 'conversation',
      lastModified: '5 hours ago',
      relevance: 0.82,
      category: 'Conversations',
      source: 'conversation',
      tags: ['performance', 'metrics', 'team'],
      description: 'Discussion thread about team performance indicators'
    },
    {
      id: 5,
      title: 'Market Research Report',
      type: 'document',
      lastModified: '1 hour ago',
      relevance: 0.91,
      category: 'Generated',
      size: 3072000,
      source: 'agent',
      tags: ['market', 'research', 'report'],
      description: 'AI-generated market research report based on latest data'
    }
  ]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Simulate agent typing
    setIsTyping(true);
    setTypingAgent('Main Coordinator');
    
    // Simulate agent response after delay
    setTimeout(() => {
      const agentResponse = {
        id: Date.now() + 1,
        type: 'agent',
        agent: 'Main Coordinator',
        content: generateAgentResponse(userMessage.content),
        timestamp: new Date().toISOString(),
        actions: ['thumbs-up', 'thumbs-down', 'retry']
      };
      
      setMessages(prev => [...prev, agentResponse]);
      setIsTyping(false);
      setTypingAgent(null);
    }, 1500 + Math.random() * 1000);
  };

  const generateAgentResponse = (userInput) => {
    const responses = [
      "I understand your request. Let me analyze this and provide you with a comprehensive response.",
      "That's an interesting question. I'll need to coordinate with our specialist agents to give you the best answer.",
      "I can help you with that. Let me break this down and provide you with actionable insights.",
      "Thank you for that information. I'm processing your request and will delegate to the appropriate specialist if needed.",
      "I see what you're looking for. Let me use my Think Tool to reason through this step by step."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleMessageAction = (messageId, action) => {
    switch (action) {
      case 'thumbs-up':
        console.log('Thumbs up for message:', messageId);
        break;
      case 'thumbs-down':
        console.log('Thumbs down for message:', messageId);
        break;
      case 'retry':
        console.log('Retry message:', messageId);
        break;
      case 'edit':
        console.log('Edit message:', messageId);
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const handleAgentSelect = (agentId) => {
    console.log('Selected agent:', agentId);
  };

  const handleKnowledgeSelect = (itemId) => {
    const item = knowledgeItems.find(k => k.id === itemId);
    if (item) {
      setInputValue(prev => prev + ` [Knowledge: ${item.title}] `);
      inputRef.current?.focus();
    }
  };

  const handleDeleteKnowledge = (itemId) => {
    const item = knowledgeItems.find(k => k.id === itemId);
    setConfirmDialog({
      title: 'Confirm Knowledge Deletion',
      message: `Are you sure you want to delete "${item?.title}"? This action cannot be undone.`,
      type: 'danger',
      impact: [
        '3 conversations reference this document',
        '2 agents have this in their context',
        'All associated metadata will be lost'
      ],
      onConfirm: () => {
        console.log('Deleting knowledge item:', itemId);
        setConfirmDialog(null);
      },
      onCancel: () => setConfirmDialog(null)
    });
  };

  const handleFileUpload = (fileData) => {
    console.log('File uploaded:', fileData);
    setUploadedFiles(prev => [...prev, fileData]);
    
    // Add to downloads list as completed
    setDownloads(prev => [...prev, {
      ...fileData,
      status: 'completed',
      source: 'Upload'
    }]);

    // Show success message
    const uploadMessage = {
      id: Date.now(),
      type: 'agent',
      agent: 'Main Coordinator',
      content: `Successfully uploaded "${fileData.name}". The file has been added to your knowledge base and is now available for analysis.`,
      timestamp: new Date().toISOString(),
      actions: ['thumbs-up', 'thumbs-down']
    };
    
    setMessages(prev => [...prev, uploadMessage]);
  };

  const handleDownload = (item) => {
    console.log('Downloading:', item);
    
    // Create download link and trigger download
    if (item.url) {
      const link = document.createElement('a');
      link.href = item.url;
      link.download = item.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      // Simulate download for demo
      console.log('Simulating download for:', item.name);
    }
  };

  const handleDownloadDelete = (downloadId) => {
    setDownloads(prev => prev.filter(d => d.id !== downloadId));
  };

  const handleDownloadPreview = (item) => {
    console.log('Previewing:', item);
    // Implement preview functionality
  };

  return (
    <div className="chat-container">
      {/* Agent Panel */}
      <div className={`chat-sidebar ${sidebarOpen ? 'open' : ''} md:relative md:translate-x-0`}>
        <AgentPanel 
          agents={agents}
          onAgentSelect={handleAgentSelect}
          onClose={() => setSidebarOpen(false)}
        />
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <MoreVertical className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-foreground">NeoV3 Enhanced AI Agent OS</h1>
              <p className="text-sm text-muted-foreground">
                {isTyping ? `${typingAgent} is typing...` : 'Ready to assist'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setKnowledgePanelOpen(!knowledgePanelOpen)}
              className="hidden md:flex"
            >
              Knowledge
            </Button>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              Online
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages custom-scrollbar">
          <MessageThread 
            messages={messages}
            isTyping={isTyping}
            typingAgent={typingAgent}
            onMessageAction={handleMessageAction}
          />
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <div className="flex gap-3">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
                className="chat-input"
                rows={1}
              />
              <div className="input-actions">
                <Button
                  variant="ghost"
                  size="sm"
                  className="btn-icon"
                  onClick={() => setShowFileUpload(true)}
                  title="Upload files"
                >
                  <Paperclip className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="btn-icon"
                  title="Voice input"
                >
                  <Mic className="w-4 h-4" />
                </Button>
                <div className="flex-1" />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim()}
                  className="btn-icon bg-primary text-primary-foreground hover:bg-primary/90"
                  title="Send message"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Panel */}
      <div className={`knowledge-panel ${knowledgePanelOpen ? 'open' : ''} md:relative md:translate-x-0 ${knowledgePanelOpen ? '' : 'hidden md:flex'}`}>
        <KnowledgePanel 
          items={knowledgeItems}
          onItemSelect={handleKnowledgeSelect}
          onItemDelete={handleDeleteKnowledge}
          onClose={() => setKnowledgePanelOpen(false)}
          onUpload={() => setShowFileUpload(true)}
          onDownload={() => setShowDownloadManager(true)}
        />
      </div>

      {/* Mobile Overlay */}
      {(sidebarOpen || knowledgePanelOpen) && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => {
            setSidebarOpen(false);
            setKnowledgePanelOpen(false);
          }}
        />
      )}

      {/* Confirmation Dialog */}
      {confirmDialog && (
        <ConfirmationDialog
          title={confirmDialog.title}
          message={confirmDialog.message}
          type={confirmDialog.type}
          impact={confirmDialog.impact}
          onConfirm={confirmDialog.onConfirm}
          onCancel={confirmDialog.onCancel}
        />
      )}

      {/* File Upload Dialog */}
      {showFileUpload && (
        <FileUpload
          onFileUpload={handleFileUpload}
          onClose={() => setShowFileUpload(false)}
          maxFiles={5}
          maxSize={10 * 1024 * 1024} // 10MB
        />
      )}

      {/* Download Manager */}
      {showDownloadManager && (
        <DownloadManager
          downloads={downloads}
          onClose={() => setShowDownloadManager(false)}
          onDownload={handleDownload}
          onDelete={handleDownloadDelete}
          onPreview={handleDownloadPreview}
        />
      )}
    </div>
  );
};

export default ChatInterface;


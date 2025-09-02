import React from 'react';
import { ThumbsUp, ThumbsDown, RotateCcw, Edit3, Copy, Share, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';

const MessageThread = ({ messages, isTyping, typingAgent, onMessageAction }) => {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const getAgentAvatar = (agentName) => {
    const avatars = {
      'Main Coordinator': '🎯',
      'Research Agent': '🔍',
      'Analysis Agent': '📊',
      'Creative Agent': '🎨',
      'Technical Agent': '⚙️'
    };
    return avatars[agentName] || '🤖';
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`message ${isUser ? 'user' : 'agent'} group animate-slide-in`}>
        <div className="flex items-start gap-3">
          {!isUser && (
            <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-sm flex-shrink-0">
              {getAgentAvatar(message.agent)}
            </div>
          )}
          
          <div className="flex-1 min-w-0">
            {!isUser && (
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium text-accent-foreground">
                  {message.agent}
                </span>
                <span className="text-xs text-muted-foreground">
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
            )}
            
            <div className={`message-bubble ${isUser ? 'user' : 'agent'}`}>
              <div className="prose prose-sm max-w-none">
                {message.content}
              </div>
            </div>
            
            {isUser && (
              <div className="message-timestamp text-right">
                {formatTimestamp(message.timestamp)}
              </div>
            )}
            
            {!isUser && message.actions && (
              <div className="message-actions">
                {message.actions.includes('thumbs-up') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="btn-icon"
                    onClick={() => onMessageAction(message.id, 'thumbs-up')}
                  >
                    <ThumbsUp className="w-3 h-3" />
                  </Button>
                )}
                {message.actions.includes('thumbs-down') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="btn-icon"
                    onClick={() => onMessageAction(message.id, 'thumbs-down')}
                  >
                    <ThumbsDown className="w-3 h-3" />
                  </Button>
                )}
                {message.actions.includes('retry') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="btn-icon"
                    onClick={() => onMessageAction(message.id, 'retry')}
                  >
                    <RotateCcw className="w-3 h-3" />
                  </Button>
                )}
                {message.actions.includes('edit') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="btn-icon"
                    onClick={() => onMessageAction(message.id, 'edit')}
                  >
                    <Edit3 className="w-3 h-3" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  className="btn-icon"
                  onClick={() => navigator.clipboard.writeText(message.content)}
                >
                  <Copy className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="btn-icon"
                >
                  <MoreHorizontal className="w-3 h-3" />
                </Button>
              </div>
            )}
          </div>
          
          {isUser && (
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-primary-foreground text-sm flex-shrink-0">
              👤
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderAgentHandoff = (fromAgent, toAgent, reason) => {
    return (
      <div className="agent-handoff animate-fade-in">
        <div className="agent-handoff-line"></div>
        <div className="agent-handoff-content">
          <div className="flex items-center gap-2">
            <span className="text-xs">
              {getAgentAvatar(fromAgent)} → {getAgentAvatar(toAgent)}
            </span>
            <span className="text-xs">
              Delegating to {toAgent}
            </span>
          </div>
          {reason && (
            <div className="text-xs text-muted-foreground mt-1">
              {reason}
            </div>
          )}
        </div>
        <div className="agent-handoff-line"></div>
      </div>
    );
  };

  const renderTypingIndicator = () => {
    if (!isTyping || !typingAgent) return null;
    
    return (
      <div className="message agent animate-fade-in">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-sm">
            {getAgentAvatar(typingAgent)}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-accent-foreground">
                {typingAgent}
              </span>
            </div>
            <div className="message-bubble agent">
              <div className="typing-indicator">
                <div className="typing-dots">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
                <span className="ml-2">Thinking...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {messages.map((message, index) => {
        const elements = [renderMessage(message)];
        
        // Add agent handoff visualization if this message triggered a delegation
        if (message.type === 'agent' && message.content.toLowerCase().includes('delegating')) {
          elements.push(
            <div key={`handoff-${message.id}`}>
              {renderAgentHandoff(message.agent, 'Analysis Agent', 'Specialized analysis required')}
            </div>
          );
        }
        
        return elements;
      })}
      
      {renderTypingIndicator()}
    </div>
  );
};

export default MessageThread;


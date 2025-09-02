import React, { useState } from 'react';
import { X, Plus, Settings, Activity, Clock, TrendingUp, User } from 'lucide-react';
import { Button } from './ui/button';

const AgentPanel = ({ agents, onAgentSelect, onClose }) => {
  const [selectedAgent, setSelectedAgent] = useState('coordinator');

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'agent-active';
      case 'busy': return 'agent-busy';
      case 'available': return 'agent-available';
      case 'offline': return 'agent-offline';
      default: return 'agent-offline';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Active';
      case 'busy': return 'Busy';
      case 'available': return 'Available';
      case 'offline': return 'Offline';
      default: return 'Unknown';
    }
  };

  const handleAgentClick = (agentId) => {
    setSelectedAgent(agentId);
    onAgentSelect(agentId);
  };

  return (
    <div className="h-full flex flex-col bg-sidebar">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-sidebar-foreground">Agents</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="md:hidden"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          {agents.filter(a => a.status === 'active').length} active, {agents.filter(a => a.status === 'available').length} available
        </p>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-card cursor-pointer group ${selectedAgent === agent.id ? 'active' : ''}`}
            onClick={() => handleAgentClick(agent.id)}
          >
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <div className="relative">
                <div className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center text-lg">
                  {agent.avatar}
                </div>
                <div className={`absolute -bottom-1 -right-1 agent-status ${agent.status}`}></div>
              </div>

              {/* Agent Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-sidebar-foreground truncate">
                    {agent.name}
                  </h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    agent.status === 'active' ? 'bg-green-100 text-green-800' :
                    agent.status === 'busy' ? 'bg-amber-100 text-amber-800' :
                    agent.status === 'available' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {getStatusText(agent.status)}
                  </span>
                </div>
                
                <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                  {agent.specialization}
                </p>

                {/* Agent Metrics */}
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {agent.responseTime}
                  </div>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {agent.successRate}%
                  </div>
                </div>
              </div>
            </div>

            {/* Expanded Details (when selected) */}
            {selectedAgent === agent.id && (
              <div className="mt-3 pt-3 border-t border-border animate-slide-in">
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-background/50 p-2 rounded">
                    <div className="text-muted-foreground">Response Time</div>
                    <div className="font-medium">{agent.responseTime}</div>
                  </div>
                  <div className="bg-background/50 p-2 rounded">
                    <div className="text-muted-foreground">Success Rate</div>
                    <div className="font-medium">{agent.successRate}%</div>
                  </div>
                </div>
                
                <div className="flex gap-2 mt-3">
                  <Button size="sm" variant="outline" className="flex-1">
                    <Activity className="w-3 h-3 mr-1" />
                    Monitor
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    <Settings className="w-3 h-3 mr-1" />
                    Configure
                  </Button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="space-y-2">
          <Button className="w-full" size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Agent
          </Button>
          <Button variant="outline" className="w-full" size="sm">
            <Settings className="w-4 h-4 mr-2" />
            Manage Agents
          </Button>
        </div>
        
        {/* System Status */}
        <div className="mt-4 p-3 bg-background/50 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">System Load</span>
            <span className="font-medium">23%</span>
          </div>
          <div className="w-full bg-border rounded-full h-2 mt-2">
            <div className="bg-primary h-2 rounded-full" style={{ width: '23%' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentPanel;


import React, { useState } from 'react';
import { Search, X, Upload, Download, File, FileText, Image, Archive, Plus, Filter, MoreVertical, Eye, Trash2, Tag, Star, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

const KnowledgePanel = ({ items, onItemSelect, onItemDelete, onClose, onUpload, onDownload }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('relevance');
  const [viewMode, setViewMode] = useState('list'); // list or grid

  const categories = [
    { id: 'all', name: 'All', count: items.length },
    { id: 'documents', name: 'Documents', count: items.filter(i => i.category === 'Documents').length },
    { id: 'conversations', name: 'Conversations', count: items.filter(i => i.category === 'Conversations').length },
    { id: 'insights', name: 'Insights', count: items.filter(i => i.category === 'Insights').length },
    { id: 'uploads', name: 'Uploads', count: items.filter(i => i.category === 'Uploads').length },
    { id: 'generated', name: 'Generated', count: items.filter(i => i.category === 'Generated').length }
  ];

  const getFileIcon = (type) => {
    switch (type) {
      case 'document': return <FileText className="w-5 h-5" />;
      case 'image': return <Image className="w-5 h-5" />;
      case 'archive': return <Archive className="w-5 h-5" />;
      case 'conversation': return <File className="w-5 h-5" />;
      case 'insight': return <Star className="w-5 h-5" />;
      default: return <File className="w-5 h-5" />;
    }
  };

  const getRelevanceColor = (relevance) => {
    if (relevance >= 0.9) return 'text-green-600 bg-green-100';
    if (relevance >= 0.7) return 'text-blue-600 bg-blue-100';
    if (relevance >= 0.5) return 'text-amber-600 bg-amber-100';
    return 'text-gray-600 bg-gray-100';
  };

  const filteredItems = items
    .filter(item => {
      const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.content?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || 
                             item.category?.toLowerCase() === selectedCategory ||
                             (selectedCategory === 'uploads' && item.source === 'upload') ||
                             (selectedCategory === 'generated' && item.source === 'agent');
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'relevance': return (b.relevance || 0) - (a.relevance || 0);
        case 'date': return new Date(b.lastModified) - new Date(a.lastModified);
        case 'name': return a.title.localeCompare(b.title);
        case 'size': return (b.size || 0) - (a.size || 0);
        default: return 0;
      }
    });

  const handleItemClick = (item) => {
    onItemSelect?.(item.id);
  };

  const handleItemAction = (item, action, e) => {
    e.stopPropagation();
    switch (action) {
      case 'preview':
        console.log('Preview item:', item.id);
        break;
      case 'download':
        onDownload?.(item);
        break;
      case 'delete':
        onItemDelete?.(item.id);
        break;
      case 'tag':
        console.log('Tag item:', item.id);
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const renderListItem = (item) => (
    <div
      key={item.id}
      className={`knowledge-item group cursor-pointer ${item.relevance >= 0.8 ? 'relevant' : ''}`}
      onClick={() => handleItemClick(item)}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-1">
          {item.thumbnail ? (
            <img
              src={item.thumbnail}
              alt={item.title}
              className="w-8 h-8 object-cover rounded"
            />
          ) : (
            <div className="w-8 h-8 bg-muted rounded flex items-center justify-center">
              {getFileIcon(item.type)}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <h4 className="text-sm font-medium text-knowledge-text truncate">
              {item.title}
            </h4>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <Button
                variant="ghost"
                size="sm"
                className="w-6 h-6 p-0"
                onClick={(e) => handleItemAction(item, 'preview', e)}
              >
                <Eye className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-6 h-6 p-0"
                onClick={(e) => handleItemAction(item, 'download', e)}
              >
                <Download className="w-3 h-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="w-6 h-6 p-0"
                onClick={(e) => handleItemAction(item, 'delete', e)}
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
          
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted-foreground">
              {item.lastModified}
            </span>
            {item.relevance && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${getRelevanceColor(item.relevance)}`}>
                {Math.round(item.relevance * 100)}%
              </span>
            )}
            {item.size && (
              <span className="text-xs text-muted-foreground">
                {formatFileSize(item.size)}
              </span>
            )}
          </div>

          {item.description && (
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {item.description}
            </p>
          )}

          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="text-xs bg-secondary text-secondary-foreground px-2 py-0.5 rounded"
                >
                  {tag}
                </span>
              ))}
              {item.tags.length > 3 && (
                <span className="text-xs text-muted-foreground">
                  +{item.tags.length - 3} more
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + sizes[i];
  };

  return (
    <div className="h-full flex flex-col bg-sidebar">
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-sidebar-foreground">Knowledge</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="md:hidden"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
        
        {/* Search */}
        <div className="relative mt-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search knowledge..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="knowledge-search pl-10"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-sidebar-border">
        {/* Categories */}
        <div className="space-y-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                selectedCategory === category.id
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'hover:bg-sidebar-accent/50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{category.name}</span>
                <span className="text-xs text-muted-foreground">
                  {category.count}
                </span>
              </div>
            </button>
          ))}
        </div>

        {/* Sort */}
        <div className="mt-4">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full px-3 py-2 bg-input border border-border rounded text-sm"
          >
            <option value="relevance">Sort by Relevance</option>
            <option value="date">Sort by Date</option>
            <option value="name">Sort by Name</option>
            <option value="size">Sort by Size</option>
          </select>
        </div>
      </div>

      {/* Items List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        {filteredItems.length === 0 ? (
          <div className="p-8 text-center">
            <File className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-sm font-medium text-foreground mb-2">
              {searchQuery ? 'No results found' : 'No knowledge items'}
            </h3>
            <p className="text-xs text-muted-foreground">
              {searchQuery 
                ? 'Try adjusting your search terms'
                : 'Upload documents or start conversations to build your knowledge base'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredItems.map(renderListItem)}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="space-y-2">
          <Button 
            className="w-full" 
            size="sm"
            onClick={onUpload}
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload Document
          </Button>
          <Button 
            variant="outline" 
            className="w-full" 
            size="sm"
            onClick={onDownload}
          >
            <Download className="w-4 h-4 mr-2" />
            Download Manager
          </Button>
          <Button 
            variant="outline" 
            className="w-full" 
            size="sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Note
          </Button>
        </div>

        {/* Quick Stats */}
        <div className="mt-4 p-3 bg-background/50 rounded-lg">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <div className="text-muted-foreground">Total Items</div>
              <div className="font-medium">{items.length}</div>
            </div>
            <div>
              <div className="text-muted-foreground">High Relevance</div>
              <div className="font-medium">
                {items.filter(i => i.relevance >= 0.8).length}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgePanel;


import React, { useState, useEffect } from 'react';
import { Download, File, FileText, Image, Archive, X, Check, AlertCircle, ExternalLink, Trash2, Eye } from 'lucide-react';
import { Button } from './ui/button';

const DownloadManager = ({ downloads, onClose, onDownload, onDelete, onPreview }) => {
  const [selectedItems, setSelectedItems] = useState([]);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  const getFileIcon = (fileType) => {
    if (fileType?.startsWith('image/')) return <Image className="w-5 h-5" />;
    if (fileType?.includes('pdf')) return <FileText className="w-5 h-5" />;
    if (fileType?.includes('zip') || fileType?.includes('rar')) return <Archive className="w-5 h-5" />;
    return <File className="w-5 h-5" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'downloading': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      case 'pending': return 'text-amber-600';
      default: return 'text-muted-foreground';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <Check className="w-4 h-4 text-green-600" />;
      case 'downloading': return <Download className="w-4 h-4 text-blue-600 animate-pulse" />;
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'pending': return <AlertCircle className="w-4 h-4 text-amber-600" />;
      default: return null;
    }
  };

  const filteredDownloads = downloads
    .filter(item => {
      if (filter === 'all') return true;
      if (filter === 'completed') return item.status === 'completed';
      if (filter === 'pending') return item.status === 'pending' || item.status === 'downloading';
      if (filter === 'failed') return item.status === 'failed';
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'date') return new Date(b.createdAt) - new Date(a.createdAt);
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'size') return (b.size || 0) - (a.size || 0);
      return 0;
    });

  const handleSelectItem = (itemId) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === filteredDownloads.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredDownloads.map(item => item.id));
    }
  };

  const handleBulkDownload = () => {
    selectedItems.forEach(itemId => {
      const item = downloads.find(d => d.id === itemId);
      if (item && item.status === 'completed') {
        onDownload?.(item);
      }
    });
    setSelectedItems([]);
  };

  const handleBulkDelete = () => {
    selectedItems.forEach(itemId => {
      onDelete?.(itemId);
    });
    setSelectedItems([]);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Download Manager</h2>
            <p className="text-sm text-muted-foreground">
              Manage your downloaded content and agent-generated files
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Filters and Actions */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              {/* Filter Buttons */}
              <div className="flex items-center gap-2">
                {['all', 'completed', 'pending', 'failed'].map(filterType => (
                  <Button
                    key={filterType}
                    variant={filter === filterType ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilter(filterType)}
                  >
                    {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
                    <span className="ml-1 text-xs">
                      ({downloads.filter(d => filterType === 'all' || d.status === filterType).length})
                    </span>
                  </Button>
                ))}
              </div>

              {/* Sort Dropdown */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-1 bg-input border border-border rounded text-sm"
              >
                <option value="date">Sort by Date</option>
                <option value="name">Sort by Name</option>
                <option value="size">Sort by Size</option>
              </select>
            </div>

            {/* Bulk Actions */}
            {selectedItems.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">
                  {selectedItems.length} selected
                </span>
                <Button size="sm" onClick={handleBulkDownload}>
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </Button>
                <Button size="sm" variant="outline" onClick={handleBulkDelete}>
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </Button>
              </div>
            )}
          </div>

          {/* Select All */}
          {filteredDownloads.length > 0 && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedItems.length === filteredDownloads.length}
                onChange={handleSelectAll}
                className="rounded border-border"
              />
              <label className="text-sm text-muted-foreground">
                Select all ({filteredDownloads.length} items)
              </label>
            </div>
          )}
        </div>

        {/* Download List */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {filteredDownloads.length === 0 ? (
            <div className="p-12 text-center">
              <Download className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No downloads found</h3>
              <p className="text-sm text-muted-foreground">
                {filter === 'all' 
                  ? 'Your downloaded files will appear here'
                  : `No ${filter} downloads found`
                }
              </p>
            </div>
          ) : (
            <div className="p-6 space-y-3">
              {filteredDownloads.map((item) => (
                <div
                  key={item.id}
                  className={`flex items-center gap-4 p-4 bg-background rounded-lg border border-border hover:shadow-sm transition-all ${
                    selectedItems.includes(item.id) ? 'ring-2 ring-primary' : ''
                  }`}
                >
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedItems.includes(item.id)}
                    onChange={() => handleSelectItem(item.id)}
                    className="rounded border-border"
                  />

                  {/* File Icon */}
                  <div className="flex-shrink-0">
                    {item.thumbnail ? (
                      <img
                        src={item.thumbnail}
                        alt={item.name}
                        className="w-12 h-12 object-cover rounded"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-muted rounded flex items-center justify-center">
                        {getFileIcon(item.type)}
                      </div>
                    )}
                  </div>

                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-sm font-medium text-foreground truncate">
                        {item.name}
                      </h4>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(item.status)}
                        <span className={`text-xs ${getStatusColor(item.status)}`}>
                          {item.status}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{formatFileSize(item.size)}</span>
                      <span>{formatDate(item.createdAt)}</span>
                      {item.source && <span>from {item.source}</span>}
                    </div>

                    {/* Progress Bar for downloading items */}
                    {item.status === 'downloading' && item.progress !== undefined && (
                      <div className="mt-2">
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${item.progress}%` }}
                          />
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {item.progress}% complete
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {item.status === 'failed' && item.error && (
                      <p className="text-xs text-red-500 mt-1">
                        {item.error}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {item.status === 'completed' && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onPreview?.(item)}
                          title="Preview"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDownload?.(item)}
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        {item.url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(item.url, '_blank')}
                            title="Open in new tab"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        )}
                      </>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete?.(item.id)}
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border">
          <div className="text-sm text-muted-foreground">
            {filteredDownloads.length} items • {downloads.filter(d => d.status === 'completed').length} completed
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            {selectedItems.length > 0 && (
              <Button onClick={handleBulkDownload}>
                Download Selected ({selectedItems.length})
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DownloadManager;


import React, { useState, useRef, useCallback } from 'react';
import { Upload, File, Image, FileText, Archive, X, Check, AlertCircle, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';

const FileUpload = ({ onFileUpload, onClose, maxFiles = 5, maxSize = 10 * 1024 * 1024 }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) return <Image className="w-5 h-5" />;
    if (fileType.includes('pdf')) return <FileText className="w-5 h-5" />;
    if (fileType.includes('zip') || fileType.includes('rar')) return <Archive className="w-5 h-5" />;
    return <File className="w-5 h-5" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    const errors = [];
    
    if (file.size > maxSize) {
      errors.push(`File size exceeds ${formatFileSize(maxSize)}`);
    }
    
    // Add more validation rules as needed
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/csv',
      'application/json',
      'image/jpeg',
      'image/png',
      'image/gif',
      'application/zip',
      'application/x-rar-compressed'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      errors.push('File type not supported');
    }
    
    return errors;
  };

  const handleFiles = useCallback((fileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      errors: validateFile(file),
      preview: null
    }));

    // Generate previews for images
    newFiles.forEach(fileObj => {
      if (fileObj.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setFiles(prev => prev.map(f => 
            f.id === fileObj.id ? { ...f, preview: e.target.result } : f
          ));
        };
        reader.readAsDataURL(fileObj.file);
      }
    });

    setFiles(prev => [...prev, ...newFiles].slice(0, maxFiles));
  }, [maxFiles]);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const uploadFiles = async () => {
    const validFiles = files.filter(f => f.errors.length === 0);
    if (validFiles.length === 0) return;

    setUploading(true);
    
    for (const fileObj of validFiles) {
      try {
        setFiles(prev => prev.map(f => 
          f.id === fileObj.id ? { ...f, status: 'uploading' } : f
        ));
        
        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 10) {
          setUploadProgress(prev => ({ ...prev, [fileObj.id]: progress }));
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setFiles(prev => prev.map(f => 
          f.id === fileObj.id ? { ...f, status: 'completed' } : f
        ));
        
        // Call the upload handler
        if (onFileUpload) {
          onFileUpload({
            id: fileObj.id,
            name: fileObj.name,
            size: fileObj.size,
            type: fileObj.type,
            url: `https://api.neov3.com/files/${fileObj.id}`, // Mock URL
            uploadedAt: new Date().toISOString()
          });
        }
        
      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === fileObj.id ? { ...f, status: 'error', error: error.message } : f
        ));
      }
    }
    
    setUploading(false);
    
    // Auto-close after successful upload
    setTimeout(() => {
      if (files.every(f => f.status === 'completed' || f.errors.length > 0)) {
        onClose?.();
      }
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-foreground">Upload Documents</h2>
            <p className="text-sm text-muted-foreground">
              Upload files to share with agents or add to knowledge base
            </p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Upload Area */}
        <div className="p-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-border hover:border-primary/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Drop files here or click to browse
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Supports PDF, Word, images, text files, and archives up to {formatFileSize(maxSize)}
            </p>
            <Button onClick={() => fileInputRef.current?.click()}>
              Select Files
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileInput}
              accept=".pdf,.doc,.docx,.txt,.csv,.json,.jpg,.jpeg,.png,.gif,.zip,.rar"
            />
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-foreground mb-3">
                Selected Files ({files.length}/{maxFiles})
              </h4>
              <div className="space-y-3 max-h-60 overflow-y-auto custom-scrollbar">
                {files.map((fileObj) => (
                  <div
                    key={fileObj.id}
                    className="flex items-center gap-3 p-3 bg-background rounded-lg border border-border"
                  >
                    {/* File Icon/Preview */}
                    <div className="flex-shrink-0">
                      {fileObj.preview ? (
                        <img
                          src={fileObj.preview}
                          alt={fileObj.name}
                          className="w-10 h-10 object-cover rounded"
                        />
                      ) : (
                        <div className="w-10 h-10 bg-muted rounded flex items-center justify-center">
                          {getFileIcon(fileObj.type)}
                        </div>
                      )}
                    </div>

                    {/* File Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-foreground truncate">
                          {fileObj.name}
                        </p>
                        <div className="flex items-center gap-2">
                          {fileObj.status === 'completed' && (
                            <Check className="w-4 h-4 text-green-500" />
                          )}
                          {fileObj.status === 'error' && (
                            <AlertCircle className="w-4 h-4 text-red-500" />
                          )}
                          {fileObj.status === 'pending' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFile(fileObj.id)}
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                      
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(fileObj.size)}
                      </p>

                      {/* Progress Bar */}
                      {fileObj.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all duration-300"
                              style={{ width: `${uploadProgress[fileObj.id] || 0}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Errors */}
                      {fileObj.errors.length > 0 && (
                        <div className="mt-1">
                          {fileObj.errors.map((error, index) => (
                            <p key={index} className="text-xs text-red-500">
                              {error}
                            </p>
                          ))}
                        </div>
                      )}

                      {/* Error Message */}
                      {fileObj.status === 'error' && fileObj.error && (
                        <p className="text-xs text-red-500 mt-1">
                          {fileObj.error}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border">
          <div className="text-sm text-muted-foreground">
            {files.filter(f => f.errors.length === 0).length} of {files.length} files ready to upload
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={uploadFiles}
              disabled={uploading || files.filter(f => f.errors.length === 0).length === 0}
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;


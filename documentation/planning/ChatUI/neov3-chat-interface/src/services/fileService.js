class FileService {
  constructor() {
    this.apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
  }

  async uploadFile(file, metadata = {}) {
    const formData = new FormData();
    const docId = `doc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    formData.append('file', file);
    
    const uploadData = {
      doc_id: docId,
      file_name: file.name,
      content_type: this.getContentType(file.name),
      metadata: {
        original_name: file.name,
        size: file.size,
        uploaded_at: new Date().toISOString(),
        ...metadata
      }
    };

    const token = localStorage.getItem('access_token');
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.apiUrl}/api/documents/enqueue`, {
      method: 'POST',
      headers,
      body: JSON.stringify(uploadData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Upload failed');
    }

    return await response.json();
  }

  async listFiles(limit = 50, offset = 0) {
    const token = localStorage.getItem('access_token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });

    const response = await fetch(`${this.apiUrl}/api/knowledge/entities?${params}`, {
      headers
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to list files');
    }

    return await response.json();
  }

  async searchFiles(query, limit = 10) {
    const token = localStorage.getItem('access_token');
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.apiUrl}/api/knowledge/search`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ query, limit })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Search failed');
    }

    return await response.json();
  }

  async deleteFile(fileId) {
    const token = localStorage.getItem('access_token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.apiUrl}/api/knowledge/entities/${fileId}`, {
      method: 'DELETE',
      headers
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Delete failed');
    }

    return await response.json();
  }

  async downloadFile(fileId, fileName) {
    const token = localStorage.getItem('access_token');
    const headers = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.apiUrl}/api/knowledge/entities/${fileId}/download`, {
      headers
    });

    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  getContentType(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    const typeMap = {
      'pdf': 'pdf',
      'doc': 'docx',
      'docx': 'docx',
      'ppt': 'pptx',
      'pptx': 'pptx',
      'xls': 'xlsx',
      'xlsx': 'xlsx',
      'html': 'html',
      'htm': 'html',
      'xml': 'xml',
      'md': 'md',
      'json': 'json',
      'png': 'png',
      'jpg': 'jpg',
      'jpeg': 'jpeg',
      'txt': 'text'
    };
    return typeMap[extension] || 'text';
  }

  validateFile(file, maxSize = 10 * 1024 * 1024) {
    const errors = [];
    
    if (file.size > maxSize) {
      errors.push(`File size exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`);
    }

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/html',
      'text/xml',
      'text/markdown',
      'application/json',
      'image/png',
      'image/jpeg',
      'text/plain'
    ];

    if (!allowedTypes.includes(file.type) && file.type !== '') {
      errors.push('File type not supported');
    }

    return errors;
  }
}

class MockFileService {
  constructor() {
    this.files = [
      {
        id: 'file-1',
        name: 'Project Requirements.pdf',
        size: 2048576,
        type: 'pdf',
        uploaded_at: '2024-01-15T10:30:00Z',
        category: 'document',
        tags: ['requirements', 'project']
      },
      {
        id: 'file-2',
        name: 'API Documentation.md',
        size: 512000,
        type: 'markdown',
        uploaded_at: '2024-01-14T15:45:00Z',
        category: 'documentation',
        tags: ['api', 'docs']
      },
      {
        id: 'file-3',
        name: 'Database Schema.sql',
        size: 256000,
        type: 'text',
        uploaded_at: '2024-01-13T09:20:00Z',
        category: 'code',
        tags: ['database', 'schema']
      },
      {
        id: 'file-4',
        name: 'User Interface Mockups.png',
        size: 1024000,
        type: 'image',
        uploaded_at: '2024-01-12T14:10:00Z',
        category: 'design',
        tags: ['ui', 'mockups']
      },
      {
        id: 'file-5',
        name: 'Meeting Notes.docx',
        size: 128000,
        type: 'document',
        uploaded_at: '2024-01-11T11:00:00Z',
        category: 'notes',
        tags: ['meeting', 'notes']
      }
    ];
  }

  async uploadFile(file, metadata = {}) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newFile = {
          id: `file-${Date.now()}`,
          name: file.name,
          size: file.size,
          type: this.getContentType(file.name),
          uploaded_at: new Date().toISOString(),
          category: metadata.category || 'document',
          tags: metadata.tags || []
        };
        
        this.files.unshift(newFile);
        
        resolve({
          enqueued: true,
          doc_id: newFile.id,
          file_path: `/app/data/input/${file.name}`,
          queue: 'documents.process'
        });
      }, 1000 + Math.random() * 2000);
    });
  }

  async listFiles(limit = 50, offset = 0) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const paginatedFiles = this.files.slice(offset, offset + limit);
        resolve({
          results: paginatedFiles,
          count: paginatedFiles.length,
          total: this.files.length
        });
      }, 300);
    });
  }

  async searchFiles(query, limit = 10) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const filteredFiles = this.files.filter(file =>
          file.name.toLowerCase().includes(query.toLowerCase()) ||
          file.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase())) ||
          file.category.toLowerCase().includes(query.toLowerCase())
        ).slice(0, limit);
        
        resolve({
          results: filteredFiles,
          count: filteredFiles.length,
          mode: 'mock'
        });
      }, 500);
    });
  }

  async deleteFile(fileId) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const index = this.files.findIndex(file => file.id === fileId);
        if (index !== -1) {
          this.files.splice(index, 1);
          resolve({ message: 'File deleted successfully' });
        } else {
          throw new Error('File not found');
        }
      }, 300);
    });
  }

  async downloadFile(fileId, fileName) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const blob = new Blob(['Mock file content for ' + fileName], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        resolve();
      }, 500);
    });
  }

  getContentType(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    const typeMap = {
      'pdf': 'pdf',
      'doc': 'document',
      'docx': 'document',
      'ppt': 'presentation',
      'pptx': 'presentation',
      'xls': 'spreadsheet',
      'xlsx': 'spreadsheet',
      'html': 'html',
      'htm': 'html',
      'xml': 'xml',
      'md': 'markdown',
      'json': 'json',
      'png': 'image',
      'jpg': 'image',
      'jpeg': 'image',
      'txt': 'text'
    };
    return typeMap[extension] || 'text';
  }

  validateFile(file, maxSize = 10 * 1024 * 1024) {
    const errors = [];
    
    if (file.size > maxSize) {
      errors.push(`File size exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`);
    }

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/html',
      'text/xml',
      'text/markdown',
      'application/json',
      'image/png',
      'image/jpeg',
      'text/plain'
    ];

    if (!allowedTypes.includes(file.type) && file.type !== '') {
      errors.push('File type not supported');
    }

    return errors;
  }
}

const useRealFileService = import.meta.env.VITE_USE_REAL_FILE_SERVICE === 'true';
export default useRealFileService ? new FileService() : new MockFileService();

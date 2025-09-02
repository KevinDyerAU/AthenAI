# NeoV3 Enhanced AI Agent OS - Professional Chat Interface

A modern, professional chat interface built with React 18, Vite, and Tailwind CSS for the NeoV3 Enhanced AI Agent OS.

## Features

- **Professional Design**: Clean, modern interface with light blue and grey color scheme
- **Agent Management**: Interactive agent panel with status indicators and metrics
- **Knowledge Base**: Integrated knowledge panel with search, filtering, and file management
- **Real-time Chat**: Message thread with typing indicators and agent handoff visualization
- **File Management**: Drag-and-drop file upload with progress tracking
- **Download Manager**: Comprehensive download management with filtering and bulk operations
- **Responsive Design**: Mobile-friendly interface with collapsible panels
- **Backend Integration**: Real-time WebSocket connections and REST API integration
- **Service Architecture**: Modular service layer with mock/real service switching
- **Authentication**: JWT-based authentication with automatic token refresh

## Components

- `ChatInterface`: Main chat interface component
- `AgentPanel`: Agent listing and management
- `MessageThread`: Chat message display and interactions
- `KnowledgePanel`: Knowledge base management
- `FileUpload`: File upload with drag-and-drop
- `DownloadManager`: Download management interface
- `ConfirmationDialog`: Reusable confirmation dialogs

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Modern web browser with ES6+ support
- NeoV3 backend services (optional, for real service integration)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env to configure API endpoints and service settings
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173` to view the chat interface.

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Configuration

### Environment Variables

- `REACT_APP_API_URL`: Backend API base URL (default: http://localhost:5000)
- `REACT_APP_USE_REAL_WEBSOCKET`: Enable real WebSocket service (default: false)
- `REACT_APP_USE_REAL_FILE_SERVICE`: Enable real file service (default: false)
- `REACT_APP_USE_REAL_AUTH_SERVICE`: Enable real authentication service (default: false)
- `REACT_APP_MAX_FILE_SIZE`: Maximum file upload size in bytes (default: 10MB)
- `REACT_APP_MAX_FILES_PER_UPLOAD`: Maximum files per upload batch (default: 5)

### Service Modes

The application supports two modes for each service:

1. **Mock Mode** (default): Uses simulated services for development and testing
2. **Real Mode**: Connects to actual NeoV3 backend services

Toggle between modes using environment variables or modify the service imports directly.

## Backend Integration

### WebSocket Service

Integrates with NeoV3 Flask-SocketIO server:

- **Events**: `connect`, `room:join`, `message:send`, `message:new`, `agent:update`
- **Authentication**: JWT token-based authentication
- **Room Management**: Conversation-based room system
- **Real-time Updates**: Agent status and message broadcasting

### File Service

Integrates with NeoV3 document processing and knowledge substrate APIs:

- **Upload**: `/api/documents/enqueue` - Queue-based document processing
- **Search**: `/api/knowledge/search` - Vector and fulltext search
- **Management**: Entity-based file operations with metadata support

### Authentication Service

Integrates with NeoV3 JWT authentication system:

- **Login/Register**: `/api/auth/login`, `/api/auth/register`
- **Token Management**: Automatic refresh with `/api/auth/refresh`
- **Profile**: User profile fetching with `/api/auth/me`
- **Security**: Secure token storage and validation

### Management Scripts

Use the provided management scripts for easy deployment:

```bash
# Using bash script
./launch-chat-ui.sh start

# Using Python manager
python3 chat-ui-manager.py start
```

## Development

The interface is built with:

- **React 18**: Modern React with hooks and functional components
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful, customizable icons

## Architecture

### Component Structure

```
src/
├── components/
│   ├── ui/
│   │   └── button.jsx          # Reusable UI button component
│   ├── AgentPanel.jsx          # Agent management and status display
│   ├── ChatInterface.jsx       # Main chat interface component
│   ├── ConfirmationDialog.jsx  # Modal confirmation dialogs
│   ├── DownloadManager.jsx     # Download queue management
│   ├── FileUpload.jsx          # File upload with drag-and-drop
│   ├── KnowledgePanel.jsx      # Knowledge base browser
│   └── MessageThread.jsx       # Chat message display
├── services/
│   ├── websocket.js            # WebSocket service (real + mock)
│   ├── fileService.js          # File operations service (real + mock)
│   ├── authService.js          # Authentication service (real + mock)
│   └── index.js                # Service manager and coordination
├── App.jsx                     # Root application component
├── App.css                     # Global styles and animations
└── main.jsx                    # Application entry point
```

### Service Architecture

The application uses a modular service architecture with the following layers:

1. **Service Manager**: Central coordination of all services
2. **Individual Services**: WebSocket, File, and Authentication services
3. **Mock/Real Toggle**: Environment-based service implementation switching
4. **Event System**: Cross-service communication and state management

The chat interface integrates with the NeoV3 Enhanced AI Agent OS through:

- WebSocket connections for real-time communication
- REST API endpoints for data management
- File upload and processing pipelines
- Authentication and authorization systems

## License

Part of the NeoV3 Enhanced AI Agent OS project.

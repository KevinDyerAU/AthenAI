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

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

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

The chat interface integrates with the NeoV3 Enhanced AI Agent OS through:

- WebSocket connections for real-time communication
- REST API endpoints for data management
- File upload and processing pipelines
- Authentication and authorization systems

## License

Part of the NeoV3 Enhanced AI Agent OS project.

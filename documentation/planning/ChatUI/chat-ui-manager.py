#!/usr/bin/env python3
"""
NeoV3 Enhanced AI Agent OS - Chat Interface Manager
Advanced Python-based UI management with port conflict resolution,
process monitoring, and integration capabilities.
"""

import os
import sys
import json
import time
import signal
import socket
import subprocess
import threading
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat-ui-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

class ChatUIManager:
    """Advanced Chat UI Manager with port conflict resolution and process management"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.project_dir = self.script_dir / "neov3-chat-interface"
        self.config_file = self.script_dir / "chat-ui-config.json"
        self.pid_file = self.script_dir / "chat-ui.pid"
        self.log_file = self.script_dir / "chat-ui.log"
        
        # Configuration
        self.default_port = 5173
        self.max_port = 5200
        self.startup_timeout = 30
        self.health_check_interval = 5
        
        # Load configuration
        self.config = self.load_config()
        
        # Process tracking
        self.process = None
        self.monitoring_thread = None
        self.shutdown_event = threading.Event()
    
    def load_config(self) -> Dict:
        """Load configuration from file or create default"""
        default_config = {
            "default_port": 5173,
            "max_port": 5200,
            "auto_open_browser": True,
            "enable_monitoring": True,
            "restart_on_failure": True,
            "max_restart_attempts": 3,
            "health_check_interval": 5,
            "startup_timeout": 30
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Save default config
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message to terminal"""
        print(f"{color}{message}{Colors.NC}")
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False
    
    def find_available_port(self, start_port: int = None, max_port: int = None) -> Optional[int]:
        """Find an available port within the specified range"""
        start_port = start_port or self.config.get('default_port', self.default_port)
        max_port = max_port or self.config.get('max_port', self.max_port)
        
        for port in range(start_port, max_port + 1):
            if self.is_port_available(port):
                return port
        return None
    
    def get_running_processes(self) -> List[Dict]:
        """Get list of running vite processes related to our project"""
        processes = []
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'vite' in line and str(self.project_dir) in line:
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            'pid': int(parts[1]),
                            'command': ' '.join(parts[10:])
                        })
        except Exception as e:
            logger.error(f"Failed to get running processes: {e}")
        
        return processes
    
    def kill_existing_processes(self):
        """Kill existing chat UI processes"""
        logger.info("Checking for existing chat UI processes...")
        
        # Kill process from PID file
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if self.is_process_running(pid):
                    logger.warning(f"Killing existing process (PID: {pid})")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)
                    
                    if self.is_process_running(pid):
                        logger.warning(f"Force killing process (PID: {pid})")
                        os.kill(pid, signal.SIGKILL)
                
                self.pid_file.unlink()
            except Exception as e:
                logger.error(f"Failed to kill process from PID file: {e}")
        
        # Kill any remaining vite processes
        processes = self.get_running_processes()
        for proc in processes:
            try:
                logger.warning(f"Killing vite process (PID: {proc['pid']})")
                os.kill(proc['pid'], signal.SIGTERM)
                time.sleep(1)
                if self.is_process_running(proc['pid']):
                    os.kill(proc['pid'], signal.SIGKILL)
            except Exception as e:
                logger.error(f"Failed to kill process {proc['pid']}: {e}")
    
    def is_process_running(self, pid: int) -> bool:
        """Check if a process is running"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Node.js not found")
            logger.info(f"Node.js version: {result.stdout.strip()}")
        except Exception:
            self.print_colored("❌ Node.js is not installed", Colors.RED)
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("npm not found")
            logger.info(f"npm version: {result.stdout.strip()}")
        except Exception:
            self.print_colored("❌ npm is not installed", Colors.RED)
            return False
        
        # Check project directory
        if not self.project_dir.exists():
            self.print_colored(f"❌ Project directory not found: {self.project_dir}", Colors.RED)
            return False
        
        # Check package.json
        package_json = self.project_dir / "package.json"
        if not package_json.exists():
            self.print_colored(f"❌ package.json not found in {self.project_dir}", Colors.RED)
            return False
        
        self.print_colored("✅ Prerequisites check passed", Colors.GREEN)
        return True
    
    def install_dependencies(self) -> bool:
        """Install npm dependencies if needed"""
        logger.info("Checking and installing dependencies...")
        
        node_modules = self.project_dir / "node_modules"
        if not node_modules.exists() or not any(node_modules.iterdir()):
            self.print_colored("📦 Installing npm dependencies...", Colors.YELLOW)
            try:
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    logger.error(f"npm install failed: {result.stderr}")
                    return False
                
                self.print_colored("✅ Dependencies installed successfully", Colors.GREEN)
            except Exception as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False
        else:
            logger.info("Dependencies already installed")
        
        return True
    
    def start_dev_server(self, port: int) -> bool:
        """Start the development server"""
        logger.info(f"Starting development server on port {port}...")
        
        try:
            # Start the server
            cmd = ['npm', 'run', 'dev', '--', '--host', '--port', str(port)]
            self.process = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.process.pid))
            
            # Wait for server to start
            start_time = time.time()
            while time.time() - start_time < self.startup_timeout:
                if not self.is_port_available(port):
                    self.print_colored("✅ Development server started successfully!", Colors.GREEN)
                    self.print_colored(f"🌐 Local URL: http://localhost:{port}", Colors.CYAN)
                    
                    # Get network IP
                    try:
                        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                        if result.returncode == 0:
                            network_ip = result.stdout.strip().split()[0]
                            self.print_colored(f"🌍 Network URL: http://{network_ip}:{port}", Colors.CYAN)
                    except Exception:
                        pass
                    
                    return True
                
                if self.process.poll() is not None:
                    logger.error("Development server process terminated unexpectedly")
                    return False
                
                time.sleep(1)
            
            logger.error("Development server failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"Failed to start development server: {e}")
            return False
    
    def monitor_process(self):
        """Monitor the development server process"""
        if not self.config.get('enable_monitoring', True):
            return
        
        restart_attempts = 0
        max_attempts = self.config.get('max_restart_attempts', 3)
        
        while not self.shutdown_event.is_set():
            if self.process and self.process.poll() is not None:
                logger.warning("Development server process terminated")
                
                if self.config.get('restart_on_failure', True) and restart_attempts < max_attempts:
                    restart_attempts += 1
                    logger.info(f"Attempting restart ({restart_attempts}/{max_attempts})")
                    
                    # Find available port
                    port = self.find_available_port()
                    if port and self.start_dev_server(port):
                        restart_attempts = 0  # Reset counter on successful restart
                    else:
                        logger.error("Failed to restart server")
                else:
                    logger.error("Max restart attempts reached or restart disabled")
                    break
            
            time.sleep(self.config.get('health_check_interval', 5))
    
    def start(self) -> bool:
        """Start the chat UI"""
        self.print_colored("🚀 Starting NeoV3 Enhanced AI Agent OS Chat Interface...", Colors.PURPLE)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Kill existing processes
        self.kill_existing_processes()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Find available port
        port = self.find_available_port()
        if not port:
            self.print_colored(f"❌ No available ports found between {self.default_port} and {self.max_port}", Colors.RED)
            return False
        
        if port != self.default_port:
            self.print_colored(f"⚠️  Default port {self.default_port} is in use, using port {port} instead", Colors.YELLOW)
        
        # Start development server
        if not self.start_dev_server(port):
            return False
        
        # Start monitoring thread
        if self.config.get('enable_monitoring', True):
            self.monitoring_thread = threading.Thread(target=self.monitor_process, daemon=True)
            self.monitoring_thread.start()
        
        # Open browser if configured
        if self.config.get('auto_open_browser', True):
            self.open_browser(port)
        
        return True
    
    def stop(self):
        """Stop the chat UI"""
        logger.info("Stopping chat UI server...")
        
        self.shutdown_event.set()
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        
        self.kill_existing_processes()
        self.print_colored("✅ Chat UI server stopped", Colors.GREEN)
    
    def restart(self):
        """Restart the chat UI"""
        self.print_colored("🔄 Restarting chat UI server...", Colors.YELLOW)
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """Show current status"""
        self.print_colored("📊 Chat UI Status:", Colors.CYAN)
        
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if self.is_process_running(pid):
                    self.print_colored(f"✅ Chat UI is running (PID: {pid})", Colors.GREEN)
                    
                    # Try to find the port
                    try:
                        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
                        for line in result.stdout.split('\n'):
                            if str(pid) in line and ':' in line:
                                port = line.split(':')[1].split()[0]
                                self.print_colored(f"🌐 Running on port: {port}", Colors.CYAN)
                                self.print_colored(f"🔗 Local URL: http://localhost:{port}", Colors.CYAN)
                                break
                    except Exception:
                        pass
                else:
                    self.print_colored("⚠️  PID file exists but process is not running", Colors.YELLOW)
                    self.pid_file.unlink()
            except Exception as e:
                logger.error(f"Failed to read PID file: {e}")
        else:
            self.print_colored("❌ Chat UI is not running", Colors.RED)
    
    def open_browser(self, port: int = None):
        """Open chat UI in browser"""
        if not port:
            # Try to find running port
            if self.pid_file.exists():
                try:
                    with open(self.pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if str(pid) in line and ':' in line:
                            port = int(line.split(':')[1].split()[0])
                            break
                except Exception:
                    pass
        
        if not port:
            self.print_colored("❌ Could not determine port. Is the server running?", Colors.RED)
            return
        
        url = f"http://localhost:{port}"
        self.print_colored(f"🌐 Opening {url} in browser...", Colors.CYAN)
        
        # Try different browser commands
        browsers = ['xdg-open', 'open', 'firefox', 'google-chrome', 'chromium']
        for browser in browsers:
            try:
                subprocess.run([browser, url], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        self.print_colored(f"Please open {url} in your browser", Colors.YELLOW)
    
    def show_logs(self, lines: int = 50):
        """Show recent logs"""
        if self.log_file.exists():
            self.print_colored(f"📋 Showing chat UI logs (last {lines} lines):", Colors.CYAN)
            try:
                result = subprocess.run(['tail', '-n', str(lines), str(self.log_file)], capture_output=True, text=True)
                print(result.stdout)
            except Exception as e:
                logger.error(f"Failed to show logs: {e}")
        else:
            self.print_colored("⚠️  No log file found", Colors.YELLOW)
    
    def configure(self):
        """Interactive configuration"""
        self.print_colored("⚙️  Chat UI Configuration", Colors.PURPLE)
        
        try:
            # Default port
            current_port = self.config.get('default_port', 5173)
            new_port = input(f"Default port [{current_port}]: ").strip()
            if new_port:
                self.config['default_port'] = int(new_port)
            
            # Auto open browser
            current_browser = self.config.get('auto_open_browser', True)
            browser_input = input(f"Auto open browser [{'y' if current_browser else 'n'}]: ").strip().lower()
            if browser_input in ['y', 'yes', 'true']:
                self.config['auto_open_browser'] = True
            elif browser_input in ['n', 'no', 'false']:
                self.config['auto_open_browser'] = False
            
            # Enable monitoring
            current_monitoring = self.config.get('enable_monitoring', True)
            monitoring_input = input(f"Enable process monitoring [{'y' if current_monitoring else 'n'}]: ").strip().lower()
            if monitoring_input in ['y', 'yes', 'true']:
                self.config['enable_monitoring'] = True
            elif monitoring_input in ['n', 'no', 'false']:
                self.config['enable_monitoring'] = False
            
            # Save configuration
            self.save_config(self.config)
            self.print_colored("✅ Configuration saved", Colors.GREEN)
            
        except KeyboardInterrupt:
            self.print_colored("\n❌ Configuration cancelled", Colors.YELLOW)
        except Exception as e:
            self.print_colored(f"❌ Configuration error: {e}", Colors.RED)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NeoV3 Enhanced AI Agent OS - Chat Interface Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 chat-ui-manager.py start     # Start the chat UI
  python3 chat-ui-manager.py stop      # Stop the chat UI
  python3 chat-ui-manager.py restart   # Restart the chat UI
  python3 chat-ui-manager.py status    # Check status
  python3 chat-ui-manager.py open      # Open in browser
  python3 chat-ui-manager.py logs      # View logs
  python3 chat-ui-manager.py config    # Configure settings
        """
    )
    
    parser.add_argument(
        'command',
        choices=['start', 'stop', 'restart', 'status', 'open', 'logs', 'config'],
        nargs='?',
        default='start',
        help='Command to execute (default: start)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Specific port to use (overrides config)'
    )
    
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not auto-open browser'
    )
    
    parser.add_argument(
        '--lines',
        type=int,
        default=50,
        help='Number of log lines to show (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = ChatUIManager()
    
    # Override config with command line arguments
    if args.port:
        manager.config['default_port'] = args.port
    if args.no_browser:
        manager.config['auto_open_browser'] = False
    
    # Handle commands
    try:
        if args.command == 'start':
            if manager.start():
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    manager.print_colored("\n🛑 Shutting down...", Colors.YELLOW)
                    manager.stop()
            else:
                sys.exit(1)
        
        elif args.command == 'stop':
            manager.stop()
        
        elif args.command == 'restart':
            if not manager.restart():
                sys.exit(1)
        
        elif args.command == 'status':
            manager.status()
        
        elif args.command == 'open':
            manager.open_browser()
        
        elif args.command == 'logs':
            manager.show_logs(args.lines)
        
        elif args.command == 'config':
            manager.configure()
    
    except KeyboardInterrupt:
        manager.print_colored("\n🛑 Operation cancelled", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


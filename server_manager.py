import subprocess
import time
class ServerManager:
    def __init__(self):
        self.server_process = None
    
    def start_server(self, params):
        """Start React dev server"""
        project_path = params.get('path', './todo-app')
        
        if self.server_process and self.server_process.poll() is None:
            return "Server is already running"
        
        try:
            cmd = f"cd {project_path} && npm start"
            self.server_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(3)  # Wait for startup
            
            if self.server_process.poll() is None:
                return "React server started at http://localhost:3000"
            else:
                return "Failed to start server"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def stop_server(self, params):
        """Stop React dev server"""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            return "Server stopped"
        return "No server running"
    
    def server_status(self, params):
        """Check server status"""
        if self.server_process and self.server_process.poll() is None:
            return "Server is running at http://localhost:3000"
        return "Server is not running"


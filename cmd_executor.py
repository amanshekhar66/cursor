import subprocess
import os
import json
import time
import pexpect
import sys
from pathlib import Path

class AutomatedCommandExecutor:
    def __init__(self):
        self.current_dir = os.getcwd()
    
    def run_commands(self, cmd_input):
        """Execute commands with full automation - no human intervention needed"""
        try:
            if isinstance(cmd_input, dict):
                cmd = cmd_input.get('cmd', '')
            else:
                cmd = cmd_input
                
            if not cmd:
                return "No command provided"
            
            print(f"🤖 Executing: {cmd}")
            
            # Handle different types of commands automatically
            if self._is_interactive_command(cmd):
                return self._handle_interactive_command(cmd)
            else:
                return self._handle_regular_command(cmd)
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _is_interactive_command(self, cmd):
        """Check if command requires interactive input"""
        interactive_keywords = [
            'create-react-app', 'npm create', 'yarn create',
            'npm install -g', 'npm init', 'git clone'
        ]
        return any(keyword in cmd.lower() for keyword in interactive_keywords)
    
    def _handle_interactive_command(self, cmd):
        """Handle commands that need interactive responses"""
        try:
            # Use pexpect for full automation
            child = pexpect.spawn(cmd, timeout=600, encoding='utf-8')
            child.logfile_read = sys.stdout
            
            responses = {
                'Ok to proceed?': 'y',
                'Overwrite?': 'y',
                'Package name:': '\r',  # Just press enter
                'Version:': '\r',
                'Description:': '\r',
                'Entry point:': '\r',
                'Test command:': '\r',
                'Git repository:': '\r',
                'Keywords:': '\r',
                'Author:': '\r',
                'License:': '\r',
                'Is this OK?': 'yes'
            }
            
            while True:
                try:
                    index = child.expect(list(responses.keys()) + [pexpect.EOF, pexpect.TIMEOUT], timeout=30)
                    
                    if index < len(responses):
                        prompt = list(responses.keys())[index]
                        response = responses[prompt]
                        print(f"🤖 Auto-responding to '{prompt}' with: {response}")
                        child.sendline(response)
                    else:
                        break
                        
                except pexpect.EOF:
                    break
                except pexpect.TIMEOUT:
                    print("🤖 Command completed or timed out")
                    break
            
            child.close()
            return "Command completed successfully"
            
        except Exception as e:
            # Fallback to subprocess with auto-yes
            return self._handle_regular_command(f"echo 'y' | {cmd}")
    
    def _handle_regular_command(self, cmd):
        """Handle regular commands"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return result.stdout.strip() or "Command executed successfully"
            else:
                return f"Command failed: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"

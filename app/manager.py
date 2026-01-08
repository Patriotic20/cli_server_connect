import paramiko
import sys
import termios
import tty
import select
from rich.console import Console

console = Console()

class SSHManager:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.channel = None
    
    def connect_interactive(self):
        """Connect with interactive shell"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.client.connect(
                self.host,
                self.port,
                self.username,
                self.password,
                timeout=10
            )
            
            console.print(f"✓ Connected to {self.username}@{self.host}:{self.port}")
            
            # Open interactive shell
            self.channel = self.client.invoke_shell()
            self.channel.settimeout(0.0)
            
            # Save local terminal settings
            oldtty = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                
                while True:
                    r, _, _ = select.select([self.channel, sys.stdin], [], [])
                    
                    if self.channel in r:
                        data = self.channel.recv(1024)
                        if not data:
                            break
                        sys.stdout.write(data.decode())
                        sys.stdout.flush()
                    
                    if sys.stdin in r:
                        data = sys.stdin.read(1)
                        if not data:
                            break
                        self.channel.send(data)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        
        except paramiko.AuthenticationException:
            console.print("[red]✗ Authentication failed! Check username/password[/red]")
        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
        finally:
            self.close()
    

    def close(self):
        """Close SSH connection"""
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()
            console.print("[yellow]Connection closed[/yellow]")
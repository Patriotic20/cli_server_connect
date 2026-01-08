import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .service import SSHDatabase
from .schemas import SSHCreateRequest, SSHUpdateRequest
from .manager import SSHManager

console = Console()

@click.group()
def cli():
    """SSH Server Connection Manager"""
    pass

@cli.command()
@click.option('--name', prompt="Server name", help='Name to save as')
@click.option('--host', prompt='Host address', help='SSH host')
@click.option('--port', prompt='Port', type=int, help='SSH port')
@click.option('--username', prompt='Username', help='SSH username')
@click.option('--password', prompt=True, hide_input=True, help='SSH password')
def save(name, host, port, username, password):
    """Save new SSH server"""
    db = SSHDatabase()
    try:
        data = SSHCreateRequest(
            name=name,
            host=host,
            port=port,
            username=username,
            password=password,
        )
        db.add_server(data)
    except ValueError as e:
        console.print(f"[red]✗ Validation error: {e}[/red]")
    finally:
        db.close()

@cli.command()
def list():
    """List all saved servers"""
    db = SSHDatabase()
    try:
        servers = db.list_servers()
        
        if not servers:
            console.print("[yellow]No servers saved yet[/yellow]")
            return
        
        table = Table(title="Saved SSH Servers")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Host", style="green")
        table.add_column("Port", style="yellow")
        table.add_column("Username", style="magenta")
        
        for server in servers:
            table.add_row(
                str(server.id),
                server.name,
                server.host,
                str(server.port),
                server.username,
            )
        
        console.print(table)
    finally:
        db.close()

@cli.command()
@click.argument('server_id', type=int)
def connect(server_id):
    """Connect to saved server"""
    db = SSHDatabase()
    try:
        server = db.get_server(server_id)
        
        if not server:
            console.print(f"[red]✗ Server '{server_id}' not found![/red]")
            return
        
        console.print(Panel(
            f"[bold]{server.name}[/bold]\n"
            f"{server.username}@{server.host}:{server.port}",
            title="Connecting",
            style="blue"
        ))
        
        ssh = SSHManager(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password
        )
        
        ssh.connect_interactive()
    finally:
        db.close()

@cli.command()
@click.argument('server_id', type=int)
def delete(server_id):
    """Delete saved server"""
    db = SSHDatabase()
    try:
        db.delete_server(server_id)
    finally:
        db.close()

@cli.command()
@click.argument('server_id', type=int)
@click.option('--name', default=None, help='New name')
@click.option('--host', default=None, help='New host')
@click.option('--port', default=None, type=int, help='New port')
@click.option('--username', default=None, help='New username')
@click.option('--password', default=None, help='New password')
@click.option('--description', default=None, help='New description')
def update(server_id, name, host, port, username, password, description):
    """Update saved server"""
    db = SSHDatabase()
    try:
        # Only include fields that are provided
        update_dict = {}
        if name is not None:
            update_dict['name'] = name
        if host is not None:
            update_dict['host'] = host
        if port is not None:
            update_dict['port'] = port
        if username is not None:
            update_dict['username'] = username
        if password is not None:
            update_dict['password'] = password
        if description is not None:
            update_dict['description'] = description
        
        if not update_dict:
            console.print("[yellow]No fields to update[/yellow]")
            return
        
        update_data = SSHUpdateRequest(**update_dict)
        db.update_server(server_id, update_data)
    except ValueError as e:
        console.print(f"[red]✗ Validation error: {e}[/red]")
    finally:
        db.close()

@cli.command()
def info():
    """Show help information"""
    info_text = """[bold cyan]SSH Connection Manager v1.0[/bold cyan]

[yellow]Commands:[/yellow]
  [bold]save[/bold]     - Save new SSH server
  [bold]list[/bold]     - List all saved servers
  [bold]connect[/bold]  - Connect to saved server (by ID)
  [bold]update[/bold]   - Update server settings
  [bold]delete[/bold]   - Delete saved server
  [bold]info[/bold]     - Show this help

[yellow]Examples:[/yellow]
  python main.py save
  python main.py list
  python main.py connect 1
  python main.py update 1 --host newhost.com
  python main.py delete 1"""
    
    console.print(Panel(info_text, title="Help", style="blue"))


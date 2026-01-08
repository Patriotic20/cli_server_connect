from sqlalchemy import update

from .database import Session, SSHServer
from .schemas import SSHCreateRequest, SSHCreateResponse, SSHUpdateRequest
from rich.console import Console

console = Console()


class SSHDatabase:
    """Database manager for SSH server operations."""

    def __init__(self):
        self.session = Session()

    def add_server(self, data: SSHCreateRequest) -> bool:
        """Add a new SSH server to the database."""
        try:
            existing = self.session.query(SSHServer).filter_by(name=data.name).first()
            if existing:
                console.print(
                    f"[red]✗ Server '{data.name}' already exists![/red]"
                )
                return False

            server = SSHServer(**data.model_dump())
            self.session.add(server)
            self.session.commit()
            console.print(f"[green]✓ Server '{data.name}' saved![/green]")
            return True

        except Exception as e:
            self.session.rollback()
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def get_server(self, id: int) -> SSHCreateResponse | None:
        """Retrieve a single SSH server by ID."""
        try:
            server = self.session.query(SSHServer).filter_by(id=id).first()
            if not server:
                return None

            return server

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return None

    def list_servers(self) -> list[SSHServer]:
        """List all saved SSH servers."""
        try:
            return self.session.query(SSHServer).all()

        except Exception as e:
            console.print(f"[red]✗ Error: {e}[/red]")
            return []

    def update_server(self, id: int, update_data: SSHUpdateRequest) -> bool:
        """Update an existing SSH server."""
        try:
            server = self.session.query(SSHServer).filter_by(id=id).first()
            if not server:
                console.print(f"[red]✗ Server '{id}' not found![/red]")
                return False

            stmt = (
                update(SSHServer)
                .where(SSHServer.id == id)
                .values(**update_data.model_dump(exclude_none=True))
            )
            self.session.execute(stmt)
            self.session.commit()
            console.print(f"[green]✓ Server '{id}' updated![/green]")
            return True

        except Exception as e:
            self.session.rollback()
            console.print(f"[red]✗ Error: {e}[/red]")
            return False

    def delete_server(self, id: int) -> bool:
        """Delete an SSH server by ID."""
        try:
            server = self.session.query(SSHServer).filter_by(id=id).first()
            if not server:
                console.print(f"[red]✗ Server '{id}' not found![/red]")
                return False

            self.session.delete(server)
            self.session.commit()
            console.print(f"[green]✓ Server '{id}' deleted![/green]")
            return True

        except Exception as e:
            self.session.rollback()
            console.print(f"[red]✗ Error: {e}[/red]")
            return False
    
    def close(self):
        """Close database session"""
        self.session.close()
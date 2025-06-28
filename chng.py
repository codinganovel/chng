#!/usr/bin/env python3
"""
chng.py - Simple AI-powered changelog generator
Usage: python chng.py <diff_file> or python chng.py --setup
"""

import json
import os
import sys
from pathlib import Path

try:
    import openai
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install openai rich")
    sys.exit(1)

console = Console()

class ChngApp:
    def __init__(self):
        self.config_file = Path.home() / ".apikey"
        self.config = self.load_config()
        
    def load_config(self):
        """Load API configuration from .apikey file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Save API configuration to .apikey file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            os.chmod(self.config_file, 0o600)
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
    
    def setup(self):
        """Setup API configuration"""
        console.clear()
        console.print("[bold blue]API Configuration Setup[/bold blue]\n")
        
        # API URL
        current_url = self.config.get('url', '')
        url = Prompt.ask(
            "API URL (e.g., https://api.openai.com/v1 or http://localhost:11434/v1)",
            default=current_url
        )
        
        # Port (optional, extracted from URL if not specified)
        current_port = self.config.get('port', '')
        port = Prompt.ask(
            "Port (leave empty to use port from URL)",
            default=str(current_port) if current_port else ""
        )
        
        # API Key
        current_key = self.config.get('key', '')
        key = Prompt.ask(
            "API Key",
            password=True,
            default=current_key
        )
        
        # Model name
        current_model = self.config.get('model', 'gpt-3.5-turbo')
        model = Prompt.ask(
            "Model name (e.g., gpt-3.5-turbo, gpt-4, llama2, mistral)",
            default=current_model
        )
        
        # Save configuration
        self.config = {
            'url': url,
            'port': port,
            'key': key,
            'model': model
        }
        
        # Warn about empty values
        warnings = []
        if not url:
            warnings.append("URL is empty")
        if not key:
            warnings.append("API key is empty")
        if not model:
            warnings.append("Model is empty")
            
        if warnings:
            console.print(f"\n[yellow]Warning: {', '.join(warnings)}[/yellow]")
            console.print("[yellow]The app may not work properly without these values.[/yellow]")
        
        self.save_config()
        console.print("\n[green]✓ Configuration saved to ~/.apikey[/green]")
        console.print(f"[blue]Using model: {model}[/blue]")
        
        # Test connection
        console.print("\n[blue]Testing API connection...[/blue]")
        if self.test_connection():
            console.print("[green]✓ Connection successful![/green]")
        else:
            console.print("[red]✗ Connection failed. Please check your settings.[/red]")
    
    def get_api_url(self):
        """Construct full API URL from config"""
        url = self.config.get('url', '').rstrip('/')
        port = self.config.get('port', '')
        
        if not url:
            return None
            
        # If port is specified separately and not already in URL
        if port and f":{port}" not in url:
            # Extract protocol and host
            if "://" in url:
                protocol, rest = url.split("://", 1)
                host = rest.split("/")[0].split(":")[0]
                path = "/" + "/".join(rest.split("/")[1:]) if "/" in rest else ""
                url = f"{protocol}://{host}:{port}{path}"
        
        return url
    
    def test_connection(self):
        """Test if API connection works"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            model = self.config.get('model', 'gpt-3.5-turbo')
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False
    
    def get_client(self):
        """Get OpenAI client with current configuration"""
        api_url = self.get_api_url()
        api_key = self.config.get('key', '')
        
        if not api_url:
            console.print("[red]Error: No API URL configured. Run with --setup[/red]")
            return None
        
        if not api_key:
            # For local servers, use dummy key
            api_key = "dummy"
        
        return openai.OpenAI(
            base_url=api_url,
            api_key=api_key
        )
    
    def generate_changelog(self, diff_content):
        """Generate changelog from diff content"""
        prompt = f"""You are an expert software developer writing a changelog entry.

Given this git diff, create a concise, well-formatted changelog entry in markdown format.

Guidelines:
- Use clear, user-facing language
- Group related changes together
- Use bullet points for multiple changes
- Follow conventional changelog format (Added, Changed, Fixed, Removed, etc.)

Diff:
```
{diff_content}
```

Generate a changelog entry:"""

        client = self.get_client()
        if not client:
            return None
            
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[green]Generating changelog...", total=None)
                
                model = self.config.get('model', 'gpt-3.5-turbo')
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                progress.update(task, completed=True)
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None
    
    def process_file(self, filepath):
        """Process a diff file and generate changelog"""
        # Read the file
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except FileNotFoundError:
            console.print(f"[red]Error: File '{filepath}' not found[/red]")
            return
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            return
        
        if not content:
            console.print("[red]Error: File is empty[/red]")
            return
        
        # Generate changelog
        console.print(f"[blue]Processing {filepath}...[/blue]")
        changelog = self.generate_changelog(content)
        
        if changelog:
            console.print("\n[bold green]Generated Changelog:[/bold green]")
            console.print("="*60)
            console.print(changelog)
            console.print("="*60)
            
            # Save to file
            output_file = Path(filepath).parent / f"changelog-{Path(filepath).stem}.md"
            try:
                with open(output_file, 'w') as f:
                    f.write(f"# Changelog\n\n{changelog}")
                console.print(f"\n[green]✓ Saved to {output_file}[/green]")
            except Exception as e:
                console.print(f"[red]Error saving changelog: {e}[/red]")

def main():
    app = ChngApp()
    
    # Parse simple command line
    if len(sys.argv) < 2:
        console.print("Usage: chng <diff_file> or chng --setup")
        sys.exit(1)
    
    if sys.argv[1] == "--setup":
        app.setup()
    else:
        # Check if API is configured
        if not app.config.get('url'):
            console.print("[yellow]No API configuration found. Running setup...[/yellow]\n")
            app.setup()
            console.print("\n[blue]Now you can run: chng <diff_file>[/blue]")
        else:
            app.process_file(sys.argv[1])

if __name__ == "__main__":
    main()
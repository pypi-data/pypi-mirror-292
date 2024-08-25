import sys
from click import argument, command, option, help_option
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from io import StringIO

from minspect.inspecting import inspect_library


@command()
@help_option('-h', '--help')
@argument("module_or_class", type=str)
@option("--depth", "-d", type=int, default=0, help="Depth to inspect")
@option("--sigs", "-s", is_flag=True, help="Include function signatures")
@option("--docs", "-doc", is_flag=True, help="Include docstrings")
@option("--code", "-c", is_flag=True, help="Include source code")
@option("--imports", "-imp", is_flag=True, help="Include imports")
@option("--all", "-a", is_flag=True, help="Include all")
@option("--markdown", "-md", is_flag=True, help="Output as markdown")
def cli(module_or_class, depth, sigs, docs, code, imports, all, markdown):
    """Inspect a Python module or class. Optionally create a markdown file."""
    console = Console()
    print(f"Debug: CLI called with module_or_class={module_or_class}, depth={depth}, sigs={sigs}, docs={docs}, code={code}, imports={imports}, all={all}, markdown={markdown}")
    try:
        if all:
            sigs = docs = code = imports = True
        print(f"Debug: sigs={sigs}, docs={docs}, code={code}, imports={imports}, all={all}")
        result = inspect_library(module_or_class, depth, sigs, docs, code, imports, all, markdown)
        print(f"Debug: Result from inspect_library: {result}")
        
        if result:
            if markdown:
                md_content = generate_markdown(result, sigs, docs, code)
                console.print(md_content)
            else:
                generate_panels(console, result, sigs, docs, code)
            return 0
        else:
            console.print(f"[bold red]Error: No result returned for module '{module_or_class}'.[/bold red]", style="red")
            return 1
    except ImportError as e:
        console.print(f"[bold red]Error importing module {module_or_class}:[/bold red] {str(e)}", style="red")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        return 1

def generate_markdown(result, sigs, docs, code):
    md_content = "# Inspection Result\n\n"
    for name, info in result.items():
        md_content += generate_markdown_section(name, info, sigs, docs, code)
    return md_content

def generate_markdown_section(name, info, sigs, docs, code, level=2):
    md_content = f"{'#' * level} {name}\n\n"
    if 'type' in info:
        md_content += f"**Type:** {info['type']}\n\n"
    if 'path' in info:
        md_content += f"**Path:** {info['path']}\n\n"
    if sigs and 'signature' in info:
        md_content += f"**Signature:**\n```python\n{info['signature']}\n```\n\n"
    if docs and 'docstring' in info:
        md_content += f"**Docstring:**\n```\n{info['docstring']}\n```\n\n"
    if code and 'code' in info:
        md_content += f"**Source Code:**\n```python\n{info['code']}\n```\n\n"
    if 'members' in info:
        for member_name, member_info in info['members'].items():
            md_content += generate_markdown_section(member_name, member_info, sigs, docs, code, level + 1)
    return md_content

def generate_panels(console, result, sigs, docs, code):
    if isinstance(result, dict):
        for name, info in result.items():
            try:
                panel_content = generate_panel_content(name, info, sigs, docs, code)
                console.print(Panel(panel_content, expand=False, width=120))
                
                if isinstance(info, dict) and 'members' in info:
                    console.print("\n[bold]Members:[/bold]")
                    for member_name, member_info in info['members'].items():
                        member_panel = generate_panel_content(member_name, member_info, sigs, docs, code)
                        console.print(Panel(member_panel, expand=False, width=120))
            except Exception as e:
                console.print(f"[bold red]Error processing {name}:[/bold red] {str(e)}")
    else:
        console.print(f"[bold red]Error:[/bold red] Expected a dictionary, but got {type(result)}")

def generate_panel_content(name, info, sigs, docs, code):
    content = f"[bold cyan]{name}[/bold cyan]\n\n"
    if isinstance(info, dict):
        if 'type' in info:
            content += f"[bold]Type:[/bold] {info['type']}\n"
        if 'path' in info:
            content += f"[bold]Path:[/bold] {info['path']}\n"
        if sigs and 'signature' in info:
            content += f"\n[bold]Signature:[/bold]\n{info['signature']}\n"
        if docs and 'docstring' in info:
            content += f"\n[bold]Docstring:[/bold]\n{info['docstring'][:500]}{'...' if len(info['docstring']) > 500 else ''}\n"
        if code and 'code' in info:
            content += f"\n[bold]Source Code:[/bold]\n{info['code'][:500]}{'...' if len(info['code']) > 500 else ''}\n"
    else:
        content += f"{info}\n"
    return content

def generate_markdown(result, sigs, docs, code):
    md_content = "# Inspection Result\n\n"
    for name, info in result.items():
        md_content += f"## {name}\n\n"
        md_content += f"**Type:** {info.get('type', 'N/A')}\n\n"
        md_content += f"**Path:** {info.get('path', 'N/A')}\n\n"
        if sigs and 'signature' in info:
            md_content += f"**Signature:**\n```python\n{info['signature']}\n```\n\n"
        if docs and 'docstring' in info:
            md_content += f"**Docstring:**\n```\n{info['docstring']}\n```\n\n"
        if code and 'code' in info:
            md_content += f"**Source Code:**\n```python\n{info['code']}\n```\n\n"
    return md_content

def generate_panels(console, result, sigs, docs, code):
    for name, info in result.items():
        panel_content = f"[bold cyan]{name}[/bold cyan]\n\n"
        panel_content += f"[bold]Type:[/bold] {info.get('type', 'N/A')}\n"
        panel_content += f"[bold]Path:[/bold] {info.get('path', 'N/A')}\n"
        if sigs and 'signature' in info:
            panel_content += f"\n[bold]Signature:[/bold]\n{info['signature']}\n"
        if docs and 'docstring' in info:
            panel_content += f"\n[bold]Docstring:[/bold]\n{info['docstring']}\n"
        if code and 'code' in info:
            panel_content += f"\n[bold]Source Code:[/bold]\n{info['code']}\n"
        console.print(Panel(panel_content, expand=False))

def generate_markdown(result, sigs, docs, code):
    md_content = "# Inspection Result\n\n"
    for name, info in result.items():
        md_content += generate_markdown_section(name, info, sigs, docs, code)
    return md_content

def generate_markdown_section(name, info, sigs, docs, code, level=2):
    md_content = f"{'#' * level} {name}\n\n"
    if 'type' in info:
        md_content += f"**Type:** {info['type']}\n\n"
    if 'path' in info:
        md_content += f"**Path:** {info['path']}\n\n"
    if sigs and 'signature' in info:
        md_content += f"**Signature:**\n```python\n{info['signature']}\n```\n\n"
    if docs and 'docstring' in info:
        md_content += f"**Docstring:**\n```\n{info['docstring']}\n```\n\n"
    if code and 'code' in info:
        md_content += f"**Source Code:**\n```python\n{info['code']}\n```\n\n"
    if 'members' in info:
        for member_name, member_info in info['members'].items():
            md_content += generate_markdown_section(member_name, member_info, sigs, docs, code, level + 1)
    return md_content

def generate_panels(console, result, sigs, docs, code):
    for name, info in result.items():
        panel_content = generate_panel_content(name, info, sigs, docs, code)
        console.print(Panel(panel_content, expand=False))
        
        if 'members' in info:
            console.print("\n[bold]Members:[/bold]")
            for member_name, member_info in info['members'].items():
                member_panel = generate_panel_content(member_name, member_info, sigs, docs, code)
                console.print(Panel(member_panel, expand=False))

def generate_panel_content(name, info, sigs, docs, code):
    content = f"[bold cyan]{name}[/bold cyan]\n\n"
    if 'type' in info:
        content += f"[bold]Type:[/bold] {info['type']}\n"
    if 'path' in info:
        content += f"[bold]Path:[/bold] {info['path']}\n"
    if sigs and 'signature' in info:
        content += f"\n[bold]Signature:[/bold]\n{info['signature']}\n"
    if docs and 'docstring' in info:
        content += f"\n[bold]Docstring:[/bold]\n{info['docstring']}\n"
    if code and 'code' in info:
        content += f"\n[bold]Source Code:[/bold]\n{info['code']}\n"
    return content

if __name__ == '__main__':
    cli()

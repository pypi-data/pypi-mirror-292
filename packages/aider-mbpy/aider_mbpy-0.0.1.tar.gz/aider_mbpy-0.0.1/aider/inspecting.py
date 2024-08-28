import inspect as inspectlib
import logging
import sys
import traceback
from importlib import import_module
from pkgutil import iter_modules
from typing import Any, Dict

import click
from rich import print
from rich.console import Console
from rich.markdown import Markdown


def load_all_modules(mod) -> list[tuple[str, Any]]:
    out = []
    try:
        for module in iter_modules(mod.__path__ if hasattr(mod, "__path__") else []):
            try:
                # Corrected line: Use mod.__name__ for the package name and module.name for the module name
                full_module_name = f"{mod.__name__}.{module.name}"
                imported_module = import_module(full_module_name)

                out.append((module.name, imported_module))
            except Exception as e:
                print(f"Error loading module {module.name}: {e}")
    except Exception as e:
        traceback.print_exc()
        print(f"Error loading modules from {mod.__name__} {e}")

    return out

def is_standard_lib(module):
    if not inspectlib.ismodule(module):
        return False
    try:
        if hasattr(module, "__name__") and  module.__name__ in sys.builtin_module_names:
            return True  # Module is a built-in module
    except Exception as e:
        traceback.print_exc()  
        print(f"Error checking if module {module.__name__} is a standard library module: {e}")
        return False

def get_root_module(module):
    if hasattr(module, "__module__"):
        return get_root_module(module.__module__)
    elif hasattr(module, "__name__"):
        return module.__name__.split(".")[0]
    elif hasattr(module, "name"):
        return module.name.split(".")[0]
    elif hasattr(module, "__package__"):
        return module.__package__
    return None

def is_imported(module, obj):
    # print(f"Checking if {obj} is imported from {module}")
    # print(f"obj: {inspectlib.getmodule(obj)}")
    # print(f"Module: {inspectlib.getmodule(module)}")
    try:
        logging.debug(f"root module of obj {obj}: {get_root_module(inspectlib.getmodule(obj))}")
        logging.debug(f"root module of module {module}: {get_root_module(inspectlib.getmodule(module))}")
        if get_root_module(inspectlib.getmodule(obj)) == get_root_module(inspectlib.getmodule(module)):
            return False

        return True
    except Exception as e:
        traceback.print_exc()
        print(f"Error checking if {obj} is imported from {module}: {e}")
        if inspectlib.getmodule(obj) is None:
            print(f"{obj} has no module")
            return False
        return True


def get_full_name(obj):
    """Returns the full package, module, and class name (if applicable) for classes, functions, modules, and class member functions."""
    if inspectlib.isclass(obj) or inspectlib.isfunction(obj):
        return f"{obj.__module__}.{obj.__name__}"
    elif inspectlib.ismethod(obj):
        # For class member functions, include the class name in the path
        class_name = obj.__self__.__class__.__name__
        return f"{obj.__module__}.{class_name}.{obj.__name__}"
    elif inspectlib.ismodule(obj):
        return obj.__name__
    else:
        return "Unknown type"

def collect_info(obj: Any, depth: int = 1, current_depth: int = 0, signatures: bool = True, docs: bool = False, code: bool = False,
    all=None, object_type=None) -> Dict[str, Any]:
    if current_depth > depth:
        return {}
    
    members_dict = {}
    members = inspectlib.getmembers(obj)
    
    if current_depth == 0:
        members += load_all_modules(obj)
    for member, member_obj in members:
        if member.startswith("__") and member.endswith("__") and member != "__init__":
            continue
        
        if is_standard_lib(member):
            continue
        if is_imported(obj, member_obj):
            continue
        if object_type and not isinstance(member_obj, object_type):
            continue
        if member.startswith("_") and not all and member != "__init__":
            continue

        
        # member_obj = getattr(obj, member)
        member_info = {}
        
        if inspectlib.isclass(member_obj) or inspectlib.ismodule(member_obj):
            member_info["type"] = "class" if inspectlib.isclass(member_obj) else "module"
            if docs:
                docstring = inspectlib.getdoc(member_obj)
                if docstring:
                    member_info["docstring"] = docstring
            member_info["path"] = get_full_name(member_obj)
            member_info["members"] = collect_info(member_obj, depth, current_depth + 1, signatures, docs, code)
            
            # Add __init__ method information for classes
            if inspectlib.isclass(member_obj):
                init_method = getattr(member_obj, '__init__', None)
                if init_method and callable(init_method):
                    init_info = {}
                    init_info["type"] = "method"
                    init_info["path"] = f"{get_full_name(member_obj)}.__init__"
                    if signatures:
                        init_info["signature"] = str(inspectlib.signature(init_method))
                    if docs:
                        init_docstring = inspectlib.getdoc(init_method)
                        if init_docstring:
                            init_info["docstring"] = init_docstring
                    member_info["members"]["__init__"] = init_info
        else:
            member_info["path"] = get_full_name(member_obj)
            member_info["type"] = "function" if inspectlib.isfunction(member_obj) else "attribute"
            if signatures and inspectlib.isfunction(member_obj):
                member_info["signature"] = str(inspectlib.signature(member_obj))
            if docs:
                docstring = inspectlib.getdoc(member_obj)
                if docstring:
                    member_info["docstring"] = docstring
            if code and inspectlib.isfunction(member_obj):
                try:
                    source_code = inspectlib.getsource(member_obj)
                    member_info["code"] = source_code
                except OSError:
                    member_info["code"] = "Source code not available"
        
        members_dict[member] = member_info
    
    return members_dict

from rich.panel import Panel
from rich.text import Text

def render_dict(members_dict: Dict[str, Any], indent: int = 0, depth=0) -> None:
    console = Console()
    for name, info in members_dict.items():
        content = f"{name}\n"
        if "type" in info:
            content += f"Type: {info['type']}\n"
        if "path" in info:
            content += f"Path: {info['path']}\n"
        if "signature" in info:
            content += f"Signature: {info['signature']}\n"
        if "docstring" in info:
            content += f"Docstring:\n{info['docstring']}\n"
        if "code" in info:
            content += f"Code:\n{info['code']}\n"
        
        panel = Panel(
            Text(content),
            title=f"{'  ' * indent}{name}",
            expand=False
        )
        console.print(panel)
        
        if "members" in info:
            render_dict(info["members"], indent + 1)


        # with Live(console=console):
        #     console.print(" " * indent + f"[bold green]{name}[/bold green]:")
        #     name = info.get("path", name)
        #     console.print(f"{' ' * (indent + 2)}[bold]Path:[/bold] {name}")
        #     if "type" in info:
        #         console.print(f"{' ' * (indent + 2)}Type:{info['type']}")
        #     if "signature" in info:
        #         console.print(f"{' ' * (indent + 2)} {info['signature']}", style="github-light")
        #     if "docstring" in info:
        #         console.print(Markdown(info["docstring"], code_theme="github-light"))
        #     if "code" in info:
        #         console.print(object=info["code"], style="github-light")
        #     if "members" in info:
        #         render_dict(info["members"], indent + 2)
        #     console.print()

def get_info(module, depth: int = 0, signatures: bool = True, docs: bool = False, code: bool = False,
                all: bool = False, object_type: str = None) -> None:
    from rich.style import Style
    console = Console()
    console.print(f"[bold cyan]{module.__name__}[/bold cyan]:")
    if docs:
        docstring = inspectlib.getdoc(module)
        if docstring:
            console.print(Markdown(docstring, style=Style(bgcolor="white", color="magenta"), code_theme="github-light", inline_code_theme="github-light"))
    collected_info = collect_info(module, depth, signatures=signatures, docs=docs, code=code, all=all, object_type=object_type)
    render_dict(collected_info)

def inspect_library(module_or_class, depth=1, signatures=True, docs=False, code=False, all=False, object_type=None):
    parts = module_or_class.split(".")
    module_name = ".".join(parts[:-1]) if len(parts) > 1 else module_or_class
    class_name = parts[-1] if len(parts) > 1 else None
    logging.debug(f"module_or_class: {module_or_class}, module_name: {module_name}, class_name: {class_name}")
    try:
        module = import_module(module_name)
        obj = module
        if class_name:
            obj = getattr(module, class_name)
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
        traceback.print_exc()
        return
    except AttributeError as e:
        module = import_module(module_name)
        for member in load_all_modules(module):
            if class_name == member[0]:
                obj = member[1]
                break

        else:
            print(f"Error accessing attribute {class_name} in {module_name}: {e}")
            traceback.print_exc()
            return
    get_info(obj, depth, signatures, docs, code, all, object_type)

@click.command()
@click.argument("module_or_class", type=str)
@click.option("--depth", "-d", default=0, help="How deep to search for members.")
@click.option("--signatures", "-s", is_flag=True, help="Include function signatures.")
@click.option("--docs", "-doc", is_flag=True, help="Include docstrings.")
@click.option("--code", "-c", is_flag=True, help="Include source code.")
def main(module_or_class, depth, signatures, docs, code):
    inspect_library(module_or_class, depth, signatures, docs, code)


if __name__ == "__main__":
    main()

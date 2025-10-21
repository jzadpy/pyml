#!/usr/bin/env python3
"""
PyML - Simple and Fast Transpiler
Focuses on correctness and maintainability over premature optimization
"""

import re
import sys
import subprocess
import os
from typing import List, Tuple
from functools import lru_cache

# Pre-compiled regex patterns
PATTERNS = {
    'function_def': re.compile(r'function\s+(\w+)\s+define\s+(.+?)\s*:'),
    'for_range': re.compile(r'for\s+(\w+)\s+in\s+range\.(.+?)\s*:'),
    'for_regular': re.compile(r'for\s+([\w,\s]+)\s+in\s+(\w+)\s*:'),
    'assignment': re.compile(r'^(\w+)\s*:\s*(.+)$'),
    'print_stmt': re.compile(r'^print:\s*(.*)$'),
}

class PyMLTranspiler:
    """Clean, maintainable PyML to Python transpiler"""
    
    def __init__(self):
        self.imports = set()
        self.output = []
        
    def transpile(self, lines: List[str]) -> str:
        """Main transpilation function"""
        # Add standard imports
        self.output.append("import sys\n")
        
        i = 0
        while i < len(lines):
            i = self._process_line(lines, i)
        
        # Add user imports at the top (after sys import)
        if self.imports:
            imports_code = "\n".join(self._get_import(pkg) for pkg in sorted(self.imports))
            self.output.insert(1, imports_code + "\n")
        
        return "".join(self.output)
    
    def _process_line(self, lines: List[str], i: int) -> int:
        """Process a single line and return next index"""
        line = lines[i]
        stripped = line.strip()
        indent = self._get_indent(line)
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            self.output.append(line + "\n")
            return i + 1
        
        # Packages section
        if stripped == 'packages:':
            return self._handle_packages(lines, i)
        
        # Function definition
        if stripped.startswith('function '):
            self._handle_function(stripped, indent)
            return i + 1
        
        # For loops
        if stripped.startswith('for '):
            self._handle_for_loop(stripped, indent)
            return i + 1
        
        # Print statement
        if stripped.startswith('print:'):
            self._handle_print(stripped, indent)
            return i + 1
        
        # Assignment (with potential YAML structures)
        if ':' in stripped and not self._is_control_flow(stripped):
            return self._handle_assignment(lines, i, stripped, indent)
        
        # Function call (ends with semicolon)
        if stripped.endswith(';'):
            self.output.append(f"{indent}{stripped[:-1]}()\n")
            return i + 1
        
        # Everything else (if/elif/else/while/expressions)
        self.output.append(f"{indent}{stripped}\n")
        return i + 1
    
    def _handle_packages(self, lines: List[str], i: int) -> int:
        """Handle packages: section"""
        base_indent = self._get_indent_level(lines[i])
        j = i + 1
        
        while j < len(lines):
            stripped = lines[j].strip()
            indent_level = self._get_indent_level(lines[j])
            
            if indent_level <= base_indent and stripped:
                break
            
            if stripped.startswith('-'):
                pkg = stripped[1:].strip()
                if pkg:
                    self.imports.add(pkg)
            j += 1
        
        return j
    
    def _handle_function(self, stripped: str, indent: str):
        """Handle function definition"""
        match = PATTERNS['function_def'].match(stripped)
        if match:
            name, args = match.groups()
            args = args.strip()
            if args == "_":
                args = ""
            self.output.append(f"{indent}def {name}({args}):\n")
    
    def _handle_for_loop(self, stripped: str, indent: str):
        """Handle for loops"""
        # Range-based loop
        match = PATTERNS['for_range'].match(stripped)
        if match:
            var, range_vals = match.groups()
            parts = range_vals.split('.')
            
            if len(parts) == 1:
                self.output.append(f"{indent}for {var} in range({parts[0]}):\n")
            elif len(parts) == 2:
                self.output.append(f"{indent}for {var} in range({parts[0]}, {parts[1]}):\n")
            elif len(parts) == 3:
                self.output.append(f"{indent}for {var} in range({parts[0]}, {parts[1]}, {parts[2]}):\n")
            return
        
        # Regular for loop
        match = PATTERNS['for_regular'].match(stripped)
        if match:
            vars_part, collection = match.groups()
            vars_part = vars_part.strip()
            
            if ',' in vars_part:
                self.output.append(f"{indent}for {vars_part} in {collection}.items():\n")
            else:
                self.output.append(f"{indent}for {vars_part} in {collection}:\n")
    
    def _handle_print(self, stripped: str, indent: str):
        """Handle print statements"""
        content = stripped[6:].strip()
        
        if not content:
            self.output.append(f"{indent}print()\n")
        elif content.startswith('"') or content.startswith("'"):
            # String literal - check for f-string
            if '{' in content and '}' in content:
                self.output.append(f"{indent}print(f{content})\n")
            else:
                self.output.append(f"{indent}print({content})\n")
        elif '{' in content and '}' in content:
            # Expression with variables
            self.output.append(f'{indent}print(f"{content}")\n')
        else:
            # Variable or expression
            self.output.append(f"{indent}print({content})\n")
    
    def _handle_assignment(self, lines: List[str], i: int, stripped: str, indent: str) -> int:
        """Handle variable assignments including YAML structures"""
        parts = stripped.split(':', 1)
        if len(parts) != 2:
            self.output.append(f"{indent}{stripped}\n")
            return i + 1
        
        var_name = parts[0].strip()
        value = parts[1].strip()
        base_indent_level = self._get_indent_level(lines[i])
        
        # Check if next line is indented (YAML structure)
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            next_indent = self._get_indent_level(next_line)
            
            # YAML list
            if next_indent > base_indent_level and next_stripped.startswith('-'):
                items = []
                j = i + 1
                
                while j < len(lines):
                    line_stripped = lines[j].strip()
                    line_indent = self._get_indent_level(lines[j])
                    
                    if line_indent <= base_indent_level:
                        break
                    
                    if line_stripped.startswith('-'):
                        item = line_stripped[1:].strip()
                        if item:
                            items.append(item)
                    j += 1
                
                self.output.append(f"{indent}{var_name} = [{', '.join(items)}]\n")
                return j
            
            # YAML dictionary
            elif next_indent > base_indent_level and ':' in next_stripped:
                items = []
                j = i + 1
                
                while j < len(lines):
                    line_stripped = lines[j].strip()
                    line_indent = self._get_indent_level(lines[j])
                    
                    if line_indent <= base_indent_level:
                        break
                    
                    if ':' in line_stripped:
                        key_val = line_stripped.split(':', 1)
                        if len(key_val) == 2:
                            key = key_val[0].strip()
                            val = key_val[1].strip()
                            items.append(f"'{key}': {val}")
                    j += 1
                
                if items:
                    self.output.append(f"{indent}{var_name} = {{{', '.join(items)}}}\n")
                    return j
        
        # Simple assignment
        if value:
            self.output.append(f"{indent}{var_name} = {value}\n")
        
        return i + 1
    
    @staticmethod
    def _get_indent(line: str) -> str:
        """Get indentation string from line"""
        return line[:len(line) - len(line.lstrip())]
    
    @staticmethod
    def _get_indent_level(line: str) -> int:
        """Get indentation level (number of spaces)"""
        return len(line) - len(line.lstrip())
    
    @staticmethod
    def _is_control_flow(stripped: str) -> bool:
        """Check if line is control flow"""
        return stripped.startswith(('if ', 'elif ', 'else:', 'while ', 'try:', 'except', 'finally:', 'with '))
    
    @lru_cache(maxsize=64)
    def _get_import(self, pkg: str) -> str:
        """Convert package name to import statement"""
        # Common optimizations
        if pkg == 'time.sleep':
            return 'from time import sleep'
        
        parts = pkg.split('.')
        if len(parts) == 1:
            return f"import {pkg}"
        elif len(parts) == 2:
            return f"from {parts[0]} import {parts[1]}"
        else:
            return f"from {'.'.join(parts[:-1])} import {parts[-1]}"


def run_pyml(file_path: str, show_transpiled: bool = False):
    """Main runner function"""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Read PyML file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Transpile
    transpiler = PyMLTranspiler()
    python_code = transpiler.transpile(lines)
    
    # If --tr flag, show transpiled code and exit
    if show_transpiled:
        print("=== Transpiled Python Code ===")
        print(python_code)
        return
    
    # Create temporary Python file
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    temp_file = f"_pyml_temp_{base_name}.py"
    
    try:
        # Write Python code
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        # Execute
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True
        )
        
        # Output results
        if result.stdout:
            print(result.stdout, end='')
        
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)
        
        sys.exit(result.returncode)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("PyML Transpiler v2.0")
        print("Usage: python pyml.py <file.pyml> [--tr]")
        print("Options:")
        print("  --tr    Show transpiled Python code without executing")
        sys.exit(1)
    
    # Parse arguments
    show_transpiled = '--tr' in sys.argv
    pyml_file = None
    
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            pyml_file = arg
            break
    
    if not pyml_file:
        print("Error: No .pyml file specified", file=sys.stderr)
        sys.exit(1)
    
    run_pyml(pyml_file, show_transpiled)
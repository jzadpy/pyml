import re
import sys
import subprocess
import os
from typing import List, Dict, Any
import ast

class PyMLOptimizedTranspiler:
    def __init__(self):
        self.imports = set()
        self.variables = {}
        self.functions = {}
        self.optimization_level = 2
        
    def optimize_expressions(self, expr: str) -> str:
        """Optimiza expresiones matemáticas y de string en tiempo de compilación"""
        # Constant folding para operaciones matemáticas simples
        try:
            # Si es una expresión matemática simple, evaluarla en compile-time
            if re.match(r'^[\d\+\-\*/\.\s\(\)]+$', expr):
                result = eval(expr)
                return str(result)
        except:
            pass
        
        # Optimizar concatenación de strings
        if '+' in expr and ('"' in expr or "'" in expr):
            # Convertir concatenación a f-string si es posible
            parts = expr.split('+')
            if len(parts) > 1:
                return f'f"{{{expr}}}"'
        
        return expr
    
    def generate_efficient_imports(self) -> List[str]:
        """Genera imports optimizados y específicos"""
        optimized_imports = []
        
        # Mapeo de imports optimizados
        import_optimizations = {
            'math': 'import math',
            'random': 'import random', 
            'time.sleep': 'from time import sleep',
            'datetime': 'from datetime import datetime',
            'os': 'import os',
            'sys': 'import sys'
        }
        
        for imp in self.imports:
            if imp in import_optimizations:
                optimized_imports.append(import_optimizations[imp])
            else:
                parts = imp.split('.')
                if len(parts) == 1:
                    optimized_imports.append(f"import {parts[0]}")
                elif len(parts) == 2:
                    optimized_imports.append(f"from {parts[0]} import {parts[1]}")
                else:
                    optimized_imports.append(f"from {'.'.join(parts[:-1])} import {parts[-1]}")
        
        return optimized_imports
    
    def optimize_loops(self, loop_type: str, var: str, iterable: str, body: List[str]) -> List[str]:
        """Optimiza loops generando código más eficiente"""
        optimized = []
        
        if loop_type == 'range':
            # Para range loops, usar range() nativo optimizado
            if '.' in iterable:
                parts = iterable.split('.')
                if len(parts) == 2:
                    optimized.append(f"for {var} in range({parts[0]}, {parts[1]}):")
                elif len(parts) == 3:
                    optimized.append(f"for {var} in range({parts[0]}, {parts[1]}, {parts[2]}):")
            else:
                optimized.append(f"for {var} in range({iterable}):")
        else:
            # Para otros loops, verificar si se puede optimizar
            if iterable in self.variables:
                var_type = type(self.variables[iterable])
                if var_type == dict:
                    if ',' in var:
                        optimized.append(f"for {var} in {iterable}.items():")
                    else:
                        optimized.append(f"for {var} in {iterable}:")
                else:
                    optimized.append(f"for {var} in {iterable}:")
            else:
                optimized.append(f"for {var} in {iterable}:")
        
        # Optimizar el cuerpo del loop
        for line in body:
            optimized.append(f"    {line}")
        
        return optimized
    
    def precompile_constants(self, lines: List[str]) -> List[str]:
        """Pre-compila constantes y expresiones estáticas"""
        optimized_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Detectar asignaciones de constantes
            if ':' in stripped and not any(stripped.startswith(kw) for kw in ["if", "for", "while", "print:"]):
                parts = stripped.split(':', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value = parts[1].strip()
                    
                    # Intentar evaluar expresiones constantes
                    try:
                        if re.match(r'^[\d\+\-\*/\.\s\(\)]+$', value):
                            computed = eval(value)
                            self.variables[var_name] = computed
                            optimized_lines.append(f"{var_name}: {computed}")
                            continue
                    except:
                        pass
                    
                    self.variables[var_name] = value
            
            optimized_lines.append(line)
        
        return optimized_lines
    
    def generate_optimized_bytecode(self, py_code: str) -> str:
        """Genera código Python optimizado para mejor rendimiento"""
        # Añadir optimizaciones específicas para rendimiento
        optimizations = [
            "# PyML Optimized Code",
            "import sys",
            "import builtins",
            "",
            "# Optimización: Cache de funciones builtin frecuentes",
            "_print = builtins.print",
            "_len = builtins.len",
            "_range = builtins.range",
            "_str = builtins.str",
            "_int = builtins.int",
            "_float = builtins.float",
            "",
            "# Reemplazar print con versión cached",
            "print = _print",
            "len = _len",
            "range = _range",
            "",
        ]
        
        return "\n".join(optimizations) + "\n" + py_code

    def transpile_optimized(self, lines: List[str]) -> str:
        """Transpilador optimizado principal"""
        # Pre-procesar y limpiar líneas
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                clean_lines.append(line.rstrip())
        
        if not clean_lines:
            return ""
        
        # Pre-compilar constantes
        clean_lines = self.precompile_constants(clean_lines)
        
        py_lines = []
        i = 0
        
        while i < len(clean_lines):
            line = clean_lines[i]
            stripped = line.strip()
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 2
            indent_str = "    " * indent_level
            
            # --- Packages (optimizado) ---
            if stripped == "packages:":
                j = i + 1
                while j < len(clean_lines):
                    pkg_line = clean_lines[j]
                    pkg_leading = len(pkg_line) - len(pkg_line.lstrip())
                    pkg_stripped = pkg_line.strip()
                    
                    if pkg_leading <= leading_spaces:
                        break
                    
                    if pkg_stripped.startswith("-"):
                        pkg = pkg_stripped[1:].strip()
                        if pkg:
                            self.imports.add(pkg)
                    j += 1
                i = j
                continue
            
            # --- Functions (optimizado) ---
            if stripped.startswith("function"):
                m = re.match(r'function\s+(\w+)\s+define\s+(.+)\s*:', stripped)
                if m:
                    fname, args = m.group(1), m.group(2).strip()
                    if args == "_":
                        args = ""
                    
                    # Añadir decorador para optimización
                    py_lines.append(f"{indent_str}def {fname}({args}):")
                    self.functions[fname] = args
                i += 1
                continue
            
            # --- For loops (optimizado) ---
            if stripped.startswith("for "):
                # Range loops optimizados
                m = re.match(r'for\s+(\w+)\s+in\s+range\.(.+?)\s*:', stripped)
                if m:
                    var, rvals = m.group(1), m.group(2)
                    parts = rvals.split(".")
                    if len(parts) == 2:
                        py_lines.append(f"{indent_str}for {var} in _range({parts[0]}, {parts[1]}):")
                    else:
                        py_lines.append(f"{indent_str}for {var} in _range({','.join(parts)}):")
                    i += 1
                    continue
                
                # Regular for loops
                m2 = re.match(r'for\s+([\w,\s]+)\s+in\s+(\w+)\s*:', stripped)
                if m2:
                    vars_, collection = m2.group(1).strip(), m2.group(2)
                    if "," in vars_:
                        py_lines.append(f"{indent_str}for {vars_} in {collection}.items():")
                    else:
                        py_lines.append(f"{indent_str}for {vars_} in {collection}:")
                    i += 1
                    continue
            
            # --- Print optimizado ---
            if stripped.startswith("print:"):
                val = stripped[6:].strip()
                if not val:
                    py_lines.append(f"{indent_str}_print()")
                elif val.startswith('"') and val.endswith('"'):
                    if "{" in val and "}" in val:
                        py_lines.append(f"{indent_str}_print(f{val})")
                    else:
                        py_lines.append(f"{indent_str}_print({val})")
                elif "{" in val and "}" in val:
                    py_lines.append(f'{indent_str}_print(f"{val}")')
                else:
                    py_lines.append(f"{indent_str}_print({val})")
                i += 1
                continue
            
            # --- Variables optimizadas ---
            if ":" in stripped and not stripped.startswith(("if ", "elif ", "else:", "while ", "for ")):
                parts = stripped.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val_part = parts[1].strip()
                    
                    # Optimizar expresiones
                    val_part = self.optimize_expressions(val_part)
                    
                    # Check for YAML structures (mantener lógica existente pero optimizada)
                    if i + 1 < len(clean_lines):
                        next_line = clean_lines[i + 1]
                        next_leading = len(next_line) - len(next_line.lstrip())
                        next_stripped = next_line.strip()
                        
                        # YAML list
                        if next_leading > leading_spaces and next_stripped.startswith("-"):
                            lst_items = []
                            j = i + 1
                            while j < len(clean_lines):
                                item_line = clean_lines[j]
                                item_leading = len(item_line) - len(item_line.lstrip())
                                item_stripped = item_line.strip()
                                
                                if item_leading <= leading_spaces:
                                    break
                                
                                if item_stripped.startswith("-"):
                                    item_content = item_stripped[1:].strip()
                                    if item_content:
                                        lst_items.append(item_content)
                                j += 1
                            
                            py_lines.append(f"{indent_str}{key} = [{', '.join(lst_items)}]")
                            self.variables[key] = lst_items
                            i = j
                            continue
                        
                        # YAML dict (similar optimization)
                        elif next_leading > leading_spaces and ":" in next_stripped:
                            dict_items = []
                            j = i + 1
                            while j < len(clean_lines):
                                dict_line = clean_lines[j]
                                dict_leading = len(dict_line) - len(dict_line.lstrip())
                                dict_stripped = dict_line.strip()
                                
                                if dict_leading <= leading_spaces:
                                    break
                                if ":" in dict_stripped:
                                    dict_parts = dict_stripped.split(":", 1)
                                    if len(dict_parts) == 2:
                                        dict_key = dict_parts[0].strip()
                                        dict_val = dict_parts[1].strip()
                                        dict_items.append(f"'{dict_key}': '{dict_val}'")
                                j += 1
                            
                            if dict_items:
                                py_lines.append(f"{indent_str}{key} = {{{', '.join(dict_items)}}}")
                            i = j
                            continue
                    
                    # Simple assignment
                    if val_part:
                        py_lines.append(f"{indent_str}{key} = {val_part}")
                        self.variables[key] = val_part
                    i += 1
                    continue
            
            # --- Function calls ---
            if stripped.endswith(";"):
                fname = stripped[:-1].strip()
                py_lines.append(f"{indent_str}{fname}()")
                i += 1
                continue
            
            # --- Control flow ---
            if any(stripped.startswith(kw) for kw in ["if ", "elif ", "else:", "while "]):
                py_lines.append(f"{indent_str}{stripped}")
                i += 1
                continue
            
            # --- Function calls with arguments ---
            if ":" in stripped and not any(stripped.startswith(kw) for kw in ["print:", "if ", "elif ", "else:", "while ", "for "]):
                parts = stripped.split(":", 1)
                if len(parts) == 2:
                    func_name = parts[0].strip()
                    arg = parts[1].strip()
                    if func_name in self.functions:
                        py_lines.append(f"{indent_str}{func_name}({arg})")
                        i += 1
                        continue
            
            # Default
            if stripped:
                py_lines.append(f"{indent_str}{stripped}")
            i += 1
        
        # Generar imports optimizados al inicio
        imports = self.generate_efficient_imports()
        
        # Combinar todo
        result = "\n".join(imports + [""] + py_lines)
        return self.generate_optimized_bytecode(result)

def run_pyml_optimized(file_path):
    """Runner optimizado para archivos PyML"""
    temp_file = "pyml_runner_temp.py"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        transpiler = PyMLOptimizedTranspiler()
        code = transpiler.transpile_optimized(lines)
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Ejecutar con optimizaciones de Python
        result = subprocess.run(
            [sys.executable, "-O", temp_file],  # -O para optimización
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script de Python:")
        print(e.stderr)
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: src/python pyml.py <archivo.pyml>")
        print("Para Linux: src/python.linux.py  <archivo.pyml>")
        sys.exit(1)
    run_pyml_optimized(sys.argv[1])



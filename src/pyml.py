#!/usr/bin/env python3
"""
PyML Ultra-Performance Runner v2.0
Maximum speed optimization with JIT, parallel processing, and advanced techniques
"""

import re
import sys
import subprocess
import os
import mmap
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache
import io
from contextlib import contextmanager
import time
import hashlib
import pickle
import tempfile

# Importaciones condicionales para máximo rendimiento
try:
    import numba
    from numba import jit, njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Patrones regex pre-compilados para máximo rendimiento
REGEX_PATTERNS = {
    'math_expr': re.compile(r'^[\d\+\-\*/\.\s\(\)]+$'),
    'function_def': re.compile(r'function\s+(\w+)\s+define\s+(.+)\s*:'),
    'for_range': re.compile(r'for\s+(\w+)\s+in\s+range\.(.+?)\s*:'),
    'for_regular': re.compile(r'for\s+([\w,\s]+)\s+in\s+(\w+)\s*:'),
    'assignment': re.compile(r'^(\w+)\s*:\s*(.+)$'),
    'print_stmt': re.compile(r'^print:\s*(.*)$'),
}

# Cache de bytecode
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'pyml_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Configuración del sistema
SYSTEM_CONFIG = {
    'cpu_count': mp.cpu_count(),
    'memory_gb': 8,  # Default
}

if HAS_PSUTIL:
    try:
        SYSTEM_CONFIG['memory_gb'] = psutil.virtual_memory().total // (1024**3)
    except:
        pass

class PerformanceProfiler:
    """Profiler simple para medir rendimiento"""
    def __init__(self):
        self.timings = {}
        self.enabled = True
    
    @contextmanager
    def time_section(self, name):
        if not self.enabled:
            yield
            return
        
        start = time.perf_counter()
        try:
            yield
        finally:
            end = time.perf_counter()
            self.timings[name] = self.timings.get(name, 0) + (end - start)
    
    def get_results(self):
        return sorted(self.timings.items(), key=lambda x: x[1], reverse=True)

# Profiler global
profiler = PerformanceProfiler()

@lru_cache(maxsize=1024)
def get_file_hash(filepath: str) -> str:
    """Hash rápido de archivos para cache"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except:
        return str(time.time())

class FastParser:
    """Parser optimizado para líneas PyML"""
    
    def __init__(self):
        self.line_cache = {}
    
    def parse_line(self, line: str) -> Tuple[str, str, int, str]:
        """Parse rápido de una línea"""
        if line in self.line_cache:
            return self.line_cache[line]
        
        stripped = line.strip()
        leading_spaces = len(line) - len(line.lstrip())
        
        # Clasificar tipo de línea
        line_type = 'unknown'
        if not stripped or stripped.startswith('#'):
            line_type = 'comment'
        elif stripped == 'packages:':
            line_type = 'packages'
        elif stripped.startswith('function'):
            line_type = 'function'
        elif stripped.startswith('for '):
            line_type = 'for'
        elif stripped.startswith('print:'):
            line_type = 'print'
        elif ':' in stripped and not stripped.startswith(('if ', 'elif ', 'else:', 'while ')):
            line_type = 'assignment'
        elif stripped.startswith(('if ', 'elif ', 'else:', 'while ')):
            line_type = 'control'
        elif stripped.endswith(';'):
            line_type = 'function_call'
        
        result = (line.rstrip(), stripped, leading_spaces, line_type)
        self.line_cache[line] = result
        return result

class UltraOptimizedTranspiler:
    """Transpilador con todas las optimizaciones"""
    
    def __init__(self):
        self.imports = set()
        self.variables = {}
        self.functions = {}
        self.constants_cache = {}
        self.code_buffer = io.StringIO()
        self.parser = FastParser()
        self.optimization_level = 3
    
    @lru_cache(maxsize=512)
    def optimize_expression(self, expr: str) -> str:
        """Optimización de expresiones con cache"""
        if expr in self.constants_cache:
            return self.constants_cache[expr]
        
        # Constant folding para matemáticas
        if REGEX_PATTERNS['math_expr'].match(expr):
            try:
                result = str(eval(expr))
                self.constants_cache[expr] = result
                return result
            except:
                pass
        
        # Optimizar concatenación de strings
        if '+' in expr and ('"' in expr or "'" in expr):
            if expr.count('+') > 2:
                self.constants_cache[expr] = f'f"{{{expr}}}"'
                return self.constants_cache[expr]
        
        self.constants_cache[expr] = expr
        return expr
    
    @lru_cache(maxsize=128)
    def get_optimized_import(self, imp: str) -> str:
        """Imports optimizados"""
        fast_imports = {
            'math': 'import math',
            'time': 'import time',
            'random': 'import random',
            'time.sleep': 'from time import sleep',
            'datetime': 'from datetime import datetime',
            'os': 'import os',
            'sys': 'import sys',
            'json': 'import json',
            're': 'import re',
        }
        
        if imp in fast_imports:
            return fast_imports[imp]
        
        parts = imp.split('.')
        if len(parts) == 1:
            return f"import {parts[0]}"
        elif len(parts) == 2:
            return f"from {parts[0]} import {parts[1]}"
        else:
            return f"from {'.'.join(parts[:-1])} import {parts[-1]}"
    
    def write_preamble(self):
        """Escribe preámbulo optimizado"""
        preamble = '''# PyML Ultra-Optimized Code
import sys
import builtins

# Cache de funciones builtin
_print = builtins.print
_len = builtins.len
_range = builtins.range
_str = builtins.str
_int = builtins.int
_float = builtins.float

# Funciones optimizadas
def fast_print(*args):
    if args:
        sys.stdout.write(' '.join(str(arg) for arg in args))
        sys.stdout.write('\\n')
    else:
        sys.stdout.write('\\n')
    sys.stdout.flush()

# Reemplazar con versiones optimizadas
print = fast_print
len = _len
range = _range
str = _str
int = _int
float = _float

'''
        self.code_buffer.write(preamble)
    
    def optimize_small_loop(self, var: str, count: int, body: List[str], indent: str) -> str:
        """Desenrolla loops muy pequeños"""
        if count <= 3:
            unrolled = []
            for i in range(count):
                for line in body:
                    optimized_line = line.replace(var, str(i))
                    unrolled.append(f"{indent}{optimized_line}")
            return "\n".join(unrolled)
        return None
    
    def parallel_parse(self, lines: List[str]) -> List[Tuple]:
        """Parse con paralelismo para archivos grandes"""
        if len(lines) < 100:  # Archivos pequeños, single-thread
            return [self.parser.parse_line(line) for line in lines]
        
        # Para archivos grandes, usar threads
        chunk_size = max(10, len(lines) // min(4, SYSTEM_CONFIG['cpu_count']))
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_chunk = {
                executor.submit(self._parse_chunk, chunk): chunk 
                for chunk in chunks
            }
            
            for future in as_completed(future_to_chunk):
                try:
                    results.extend(future.result())
                except Exception:
                    # Fallback
                    chunk = future_to_chunk[future]
                    results.extend([self.parser.parse_line(line) for line in chunk])
        
        return results
    
    def _parse_chunk(self, chunk: List[str]) -> List[Tuple]:
        """Parse un chunk de líneas"""
        return [self.parser.parse_line(line) for line in chunk]
    
    def transpile_optimized(self, lines: List[str]) -> str:
        """Transpilación principal optimizada"""
        with profiler.time_section('parsing'):
            parsed_lines = self.parallel_parse(lines)
        
        if not parsed_lines:
            return ""
        
        with profiler.time_section('preamble'):
            self.write_preamble()
        
        with profiler.time_section('transpilation'):
            self._process_lines(parsed_lines)
        
        with profiler.time_section('post_processing'):
            return self._finalize_code()
    
    def _process_lines(self, parsed_lines: List[Tuple]):
        """Procesa las líneas parseadas"""
        i = 0
        while i < len(parsed_lines):
            full_line, stripped, leading_spaces, line_type = parsed_lines[i]
            indent_level = leading_spaces // 2
            indent_str = "    " * indent_level
            
            if line_type == 'comment':
                i += 1
                continue
            elif line_type == 'packages':
                i = self._handle_packages(parsed_lines, i, leading_spaces)
            elif line_type == 'function':
                i = self._handle_function(stripped, indent_str, i)
            elif line_type == 'for':
                i = self._handle_for_loop(parsed_lines, i, stripped, indent_str, leading_spaces)
            elif line_type == 'print':
                self._handle_print(stripped, indent_str)
                i += 1
            elif line_type == 'assignment':
                i = self._handle_assignment(parsed_lines, i, stripped, indent_str, leading_spaces)
            elif line_type == 'function_call':
                self._handle_function_call(stripped, indent_str)
                i += 1
            elif line_type == 'control':
                self.code_buffer.write(f"{indent_str}{stripped}\n")
                i += 1
            else:
                if stripped:
                    self.code_buffer.write(f"{indent_str}{stripped}\n")
                i += 1
    
    def _handle_packages(self, parsed_lines: List[Tuple], i: int, leading_spaces: int) -> int:
        """Maneja sección packages"""
        j = i + 1
        while j < len(parsed_lines):
            _, pkg_stripped, pkg_leading, _ = parsed_lines[j]
            if pkg_leading <= leading_spaces:
                break
            if pkg_stripped.startswith("-"):
                pkg = pkg_stripped[1:].strip()
                if pkg:
                    self.imports.add(pkg)
            j += 1
        return j
    
    def _handle_function(self, stripped: str, indent_str: str, i: int) -> int:
        """Maneja definición de función"""
        m = REGEX_PATTERNS['function_def'].match(stripped)
        if m:
            fname, args = m.group(1), m.group(2).strip()
            if args == "_":
                args = ""
            self.code_buffer.write(f"{indent_str}def {fname}({args}):\n")
            self.functions[fname] = args
        return i + 1
    
    def _handle_for_loop(self, parsed_lines: List[Tuple], i: int, stripped: str, indent_str: str, leading_spaces: int) -> int:
        """Maneja for loops con optimizaciones"""
        # Range loops
        m = REGEX_PATTERNS['for_range'].match(stripped)
        if m:
            var, rvals = m.group(1), m.group(2)
            parts = rvals.split(".")
            
            # Recoger cuerpo del loop
            loop_body = []
            j = i + 1
            while j < len(parsed_lines):
                if j >= len(parsed_lines):
                    break
                _, body_stripped, body_leading, _ = parsed_lines[j]
                if body_leading <= leading_spaces:
                    break
                loop_body.append(body_stripped)
                j += 1
            
            # Intentar desenrollado para loops muy pequeños
            if len(parts) == 1 and parts[0].isdigit():
                n = int(parts[0])
                unrolled = self.optimize_small_loop(var, n, loop_body, indent_str + "    ")
                if unrolled:
                    self.code_buffer.write(f"{unrolled}\n")
                    return j
            
            # Loop normal
            if len(parts) == 2:
                self.code_buffer.write(f"{indent_str}for {var} in range({parts[0]}, {parts[1]}):\n")
            else:
                self.code_buffer.write(f"{indent_str}for {var} in range({parts[0]}):\n")
            return i + 1
        
        # Regular for loops
        m2 = REGEX_PATTERNS['for_regular'].match(stripped)
        if m2:
            vars_, collection = m2.group(1).strip(), m2.group(2)
            if "," in vars_:
                self.code_buffer.write(f"{indent_str}for {vars_} in {collection}.items():\n")
            else:
                self.code_buffer.write(f"{indent_str}for {vars_} in {collection}:\n")
            return i + 1
        
        return i + 1
    
    def _handle_print(self, stripped: str, indent_str: str):
        """Maneja print optimizado"""
        val = stripped[6:].strip()
        if not val:
            self.code_buffer.write(f"{indent_str}fast_print()\n")
        elif val.startswith('"') and val.endswith('"'):
            if "{" in val and "}" in val:
                self.code_buffer.write(f"{indent_str}fast_print(f{val})\n")
            else:
                self.code_buffer.write(f"{indent_str}fast_print({val})\n")
        elif "{" in val and "}" in val:
            self.code_buffer.write(f'{indent_str}fast_print(f"{val}")\n')
        else:
            self.code_buffer.write(f"{indent_str}fast_print({val})\n")
    
    def _handle_assignment(self, parsed_lines: List[Tuple], i: int, stripped: str, indent_str: str, leading_spaces: int) -> int:
        """Maneja asignaciones"""
        parts = stripped.split(":", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            val_part = parts[1].strip()
            
            # Optimizar expresión
            val_part = self.optimize_expression(val_part)
            
            # Verificar estructuras YAML
            if i + 1 < len(parsed_lines):
                _, next_stripped, next_leading, _ = parsed_lines[i + 1]
                
                # YAML list
                if next_leading > leading_spaces and next_stripped.startswith("-"):
                    lst_items = []
                    j = i + 1
                    while j < len(parsed_lines):
                        if j >= len(parsed_lines):
                            break
                        _, item_stripped, item_leading, _ = parsed_lines[j]
                        
                        if item_leading <= leading_spaces:
                            break
                        
                        if item_stripped.startswith("-"):
                            item_content = item_stripped[1:].strip()
                            if item_content:
                                item_content = self.optimize_expression(item_content)
                                lst_items.append(item_content)
                        j += 1
                    
                    self.code_buffer.write(f"{indent_str}{key} = [{', '.join(lst_items)}]\n")
                    self.variables[key] = lst_items
                    return j
                
                # YAML dict
                elif next_leading > leading_spaces and ":" in next_stripped:
                    dict_items = []
                    j = i + 1
                    while j < len(parsed_lines):
                        if j >= len(parsed_lines):
                            break
                        _, dict_stripped, dict_leading, _ = parsed_lines[j]
                        
                        if dict_leading <= leading_spaces:
                            break
                        if ":" in dict_stripped:
                            dict_parts = dict_stripped.split(":", 1)
                            if len(dict_parts) == 2:
                                dict_key = dict_parts[0].strip()
                                dict_val = dict_parts[1].strip()
                                dict_val = self.optimize_expression(dict_val)
                                dict_items.append(f"'{dict_key}': {dict_val}")
                        j += 1
                    
                    if dict_items:
                        self.code_buffer.write(f"{indent_str}{key} = {{{', '.join(dict_items)}}}\n")
                    return j
            
            # Asignación simple
            if val_part:
                self.code_buffer.write(f"{indent_str}{key} = {val_part}\n")
                self.variables[key] = val_part
        
        return i + 1
    
    def _handle_function_call(self, stripped: str, indent_str: str):
        """Maneja llamadas a función"""
        fname = stripped[:-1].strip()
        self.code_buffer.write(f"{indent_str}{fname}()\n")
    
    def _finalize_code(self) -> str:
        """Finaliza el código con imports"""
        if self.imports:
            imports_code = "\n".join(self.get_optimized_import(imp) for imp in self.imports)
            result = self.code_buffer.getvalue()
            
            # Insertar imports después del preámbulo
            lines = result.split('\n')
            for idx, line in enumerate(lines):
                if line.strip() == '# Cache de funciones builtin':
                    lines.insert(idx, imports_code)
                    lines.insert(idx + 1, "")
                    break
            
            return '\n'.join(lines)
        
        return self.code_buffer.getvalue()

@contextmanager
def fast_file_reader(file_path):
    """Lectura optimizada de archivos"""
    try:
        file_size = os.path.getsize(file_path)
        if file_size < 1024 * 1024:  # < 1MB, lectura directa
            with open(file_path, "r", encoding="utf-8") as f:
                yield f.read()
        else:
            # Memory mapping para archivos grandes
            with open(file_path, "r+b") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    yield mm.read().decode('utf-8')
    except:
        # Fallback
        with open(file_path, "r", encoding="utf-8") as f:
            yield f.read()

def run_pyml_ultra_optimized(file_path: str):
    """Runner principal ultra-optimizado"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    temp_file = f"pyml_ultra_{base_name}_{os.getpid()}.py"
    
    execution_start = time.perf_counter()
    
    try:
        # Lectura del archivo
        with profiler.time_section('file_reading'):
            with fast_file_reader(file_path) as content:
                lines = content.splitlines()
        
        # Transpilación
        with profiler.time_section('total_transpilation'):
            transpiler = UltraOptimizedTranspiler()
            code = transpiler.transpile_optimized(lines)
        
        # Escribir archivo temporal
        with profiler.time_section('file_writing'):
            with open(temp_file, "w", encoding="utf-8", buffering=8192) as f:
                f.write(code)
        
        # Ejecución optimizada
        with profiler.time_section('execution'):
            env = os.environ.copy()
            env.update({
                'PYTHONOPTIMIZE': '2',
                'PYTHONDONTWRITEBYTECODE': '1',
                'PYTHONUNBUFFERED': '1',
            })
            
            result = subprocess.run(
                [sys.executable, "-O", "-OO", temp_file],
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            
            if result.stdout:
                sys.stdout.write(result.stdout)
                sys.stdout.flush()
            
            if result.stderr:
                sys.stderr.write(result.stderr)
                sys.stderr.flush()
    
    except FileNotFoundError:
        sys.stderr.write(f"Error: Archivo '{file_path}' no encontrado.\n")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error de ejecución:\n{e.stderr}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    finally:
        # Cleanup y métricas
        execution_end = time.perf_counter()
        total_time = execution_end - execution_start
        
        # Cleanup
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except:
            pass
        
        # Mostrar métricas si está habilitado
        if os.environ.get('PYML_SHOW_PERF', '').lower() in ('1', 'true'):
            sys.stderr.write(f"\n=== PyML Performance ===\n")
            sys.stderr.write(f"Total: {total_time:.4f}s\n")
            
            for section, timing in profiler.get_results()[:3]:
                percentage = (timing / total_time) * 100
                sys.stderr.write(f"{section}: {timing:.4f}s ({percentage:.1f}%)\n")



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("PyML Ultra-Performance Runner v2.0")
        print("Usage: python pyml_ultra_runner.py <file.pyml> [--benchmark] [--show-perf]")
        sys.exit(1)
    
 
        
        # Encontrar archivo .pyml
        pyml_file = None
        for arg in sys.argv[1:]:
            if not arg.startswith("--"):
                pyml_file = arg
                break
        
        if not pyml_file:
            print("Error: No se especificó archivo .pyml")
            sys.exit(1)
        
        run_pyml_ultra_optimized(pyml_file)
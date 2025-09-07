import re
import sys
import subprocess
import os

def transpile(lines):
    py_lines = []
    
    # Filtrar lÃ­neas vacÃ­as y comentarios
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            clean_lines.append(line.rstrip())
    
    if not clean_lines:
        return ""

    i = 0
    while i < len(clean_lines):
        line = clean_lines[i]
        stripped = line.strip()
        leading_spaces = len(line) - len(line.lstrip())
        
        # Calcular indentaciÃ³n Python
        indent_level = leading_spaces // 2
        indent_str = "    " * indent_level

        # --- Packages ---
        if stripped == "packages:":
            j = i + 1
            # Procesar todos los packages
            while j < len(clean_lines):
                pkg_line = clean_lines[j]
                pkg_leading = len(pkg_line) - len(pkg_line.lstrip())
                pkg_stripped = pkg_line.strip()
                
                # Si la indentaciÃ³n es menor o igual, salir
                if pkg_leading <= leading_spaces:
                    break
                    
                # Si es un item de la lista
                if pkg_stripped.startswith("-"):
                    pkg = pkg_stripped[1:].strip()
                    if pkg:  # Solo si hay contenido
                        parts = pkg.split(".")
                        if len(parts) == 1:
                            py_lines.append(f"import {parts[0]}")
                        elif len(parts) == 2:
                            py_lines.append(f"import {parts[0]} as {parts[1]}")
                        elif len(parts) == 3:
                            py_lines.append(f"from {parts[0]} import {parts[1]} as {parts[2]}")
                j += 1
            i = j
            continue

        # --- Functions ---
        if stripped.startswith("function"):
            m = re.match(r'function\s+(\w+)\s+define\s+(.+)\s*:', stripped)
            if m:
                fname, args = m.group(1), m.group(2).strip()
                if args == "_":
                    args = ""
                py_lines.append(f"{indent_str}def {fname}({args}):")
            i += 1
            continue

        # --- For loops ---
        if stripped.startswith("for "):
            # Range loops
            m = re.match(r'for\s+(\w+)\s+in\s+range\.(.+?)\s*:', stripped)
            if m:
                var, rvals = m.group(1), m.group(2)
                parts = rvals.split(".")
                py_lines.append(f"{indent_str}for {var} in range({','.join(parts)}):")
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

        # --- Control flow ---
        if any(stripped.startswith(kw) for kw in ["if ", "elif ", "else:", "else ", "while "]):
            py_lines.append(f"{indent_str}{stripped}")
            i += 1
            continue

        # --- Function calls ---
        if stripped.endswith(";"):
            fname = stripped[:-1].strip()
            py_lines.append(f"{indent_str}{fname}()")
            i += 1
            continue
        
        # --- Print statements ---
        if stripped.startswith("print:"):
            val = stripped[6:].strip()  # Remover "print:"
            if not val:
                py_lines.append(f"{indent_str}print()")
            elif val.startswith('"') and val.endswith('"'):
                # String literal con comillas dobles
                if "{" in val and "}" in val:
                    # Es un f-string
                    py_lines.append(f"{indent_str}print(f{val})")
                else:
                    # String normal
                    py_lines.append(f"{indent_str}print({val})")
            elif val.startswith("'") and val.endswith("'"):
                # String literal con comillas simples
                if "{" in val and "}" in val:
                    # Es un f-string
                    py_lines.append(f"{indent_str}print(f{val})")
                else:
                    # String normal
                    py_lines.append(f"{indent_str}print({val})")
            elif "{" in val and "}" in val:
                # F-string sin comillas - aÃ±adir comillas y f
                py_lines.append(f'{indent_str}print(f"{val}")')
            else:
                # Variable simple
                py_lines.append(f"{indent_str}print({val})")
            i += 1
            continue

        # --- Variables, lists, and dicts ---
        if ":" in stripped and not stripped.startswith(("if ", "elif ", "else:", "while ", "for ")):
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                val_part = parts[1].strip()
                
                # Check if next lines form a YAML structure
                if i + 1 < len(clean_lines):
                    next_line = clean_lines[i + 1]
                    next_leading = len(next_line) - len(next_line.lstrip())
                    next_stripped = next_line.strip()
                    
                    # YAML-style list
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
                                # Check if this item has properties (is a dict)
                                item_content = item_stripped[1:].strip()
                                
                                # Look ahead to see if next lines are dict properties
                                k = j + 1
                                dict_props = []
                                has_dict_props = False
                                
                                while k < len(clean_lines):
                                    prop_line = clean_lines[k]
                                    prop_leading = len(prop_line) - len(prop_line.lstrip())
                                    prop_stripped = prop_line.strip()
                                    
                                    # If same or less indentation than current item, stop
                                    if prop_leading <= item_leading:
                                        break
                                    
                                    # If it's a key:value pair at the right indentation
                                    if ":" in prop_stripped and not prop_stripped.startswith("-"):
                                        has_dict_props = True
                                        prop_parts = prop_stripped.split(":", 1)
                                        prop_key = prop_parts[0].strip()
                                        prop_val = prop_parts[1].strip()
                                        
                                        # Format the value appropriately
                                        if prop_val.startswith('"') and prop_val.endswith('"'):
                                            dict_props.append(f"'{prop_key}': {prop_val}")
                                        elif prop_val.startswith("'") and prop_val.endswith("'"):
                                            dict_props.append(f"'{prop_key}': {prop_val}")
                                        elif prop_val.isdigit() or (prop_val.replace(".", "").isdigit() and prop_val.count(".") <= 1):
                                            dict_props.append(f"'{prop_key}': {prop_val}")
                                        elif prop_val.lower() in ['true', 'false']:
                                            dict_props.append(f"'{prop_key}': {prop_val.title()}")
                                        else:
                                            dict_props.append(f"'{prop_key}': '{prop_val}'")
                                    k += 1
                                
                                if has_dict_props:
                                    # Add the item content if any
                                    if item_content:
                                        if item_content.startswith('"') and item_content.endswith('"'):
                                            dict_props.insert(0, f"'item': {item_content}")
                                        else:
                                            dict_props.insert(0, f"'item': '{item_content}'")
                                    lst_items.append("{" + ", ".join(dict_props) + "}")
                                    j = k
                                else:
                                    # Simple list item
                                    if item_content:
                                        lst_items.append(item_content)
                                    j += 1
                            else:
                                j += 1
                        
                        py_lines.append(f"{indent_str}{key} = [{', '.join(lst_items)}]")
                        i = j
                        continue

                    # YAML-style dict
                    elif next_leading > leading_spaces and ":" in next_stripped and not next_stripped.startswith("-"):
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
                                    
                                    # Format the value appropriately
                                    if dict_val.startswith('"') and dict_val.endswith('"'):
                                        dict_items.append(f"'{dict_key}': {dict_val}")
                                    elif dict_val.startswith("'") and dict_val.endswith("'"):
                                        dict_items.append(f"'{dict_key}': {dict_val}")
                                    elif dict_val.isdigit() or dict_val.replace(".", "").isdigit():
                                        dict_items.append(f"'{dict_key}': {dict_val}")
                                    else:
                                        dict_items.append(f"'{dict_key}': '{dict_val}'")
                            j += 1
                        if dict_items:
                            py_lines.append(f"{indent_str}{key} = {{{', '.join(dict_items)}}}")
                        i = j
                        continue

                # Simple assignment
                if val_part:
                    py_lines.append(f"{indent_str}{key} = {val_part}")
                i += 1
                continue

        # --- Function calls with arguments ---
        if ":" in stripped and not any(stripped.startswith(kw) for kw in ["print:", "if ", "elif ", "else:", "while ", "for "]):
            # Check if it's a function call like greet: "World"
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                func_name = parts[0].strip()
                arg = parts[1].strip()
                # Simple heuristic: if it looks like a function call
                if arg and (arg.startswith('"') or arg.startswith("'") or arg.isdigit()):
                    py_lines.append(f"{indent_str}{func_name}({arg})")
                    i += 1
                    continue

        # Default: treat as regular Python line
        if stripped:
            py_lines.append(f"{indent_str}{stripped}")
        i += 1
    
    return "\n".join(py_lines)

def run_pyml(file_path):
    temp_file = "pyml_temp.py"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        code = transpile(lines)
        
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)

        result = subprocess.run(
            [sys.executable, temp_file],
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
        print("Uso: python pyml_runner.py <nombre_de_archivo.pyml>")
        sys.exit(1)
    run_pyml(sys.argv[1])


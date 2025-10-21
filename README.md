# PyML 🐍✨

**Python con sintaxis estilo YAML - Código limpio, legible y fácil de aprender**

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: YAML-like](https://img.shields.io/badge/syntax-YAML--like-green.svg)](https://yaml.org/)

PyML es un **transpilador** que permite escribir código Python usando una sintaxis inspirada en YAML. Combina la potencia de Python con la simplicidad y legibilidad de YAML, creando una experiencia de programación más limpia y accesible.

## ✨ Características

- **🎯 Sintaxis declarativa**: Estructura clara inspirada en YAML
- **⚡ Transpilación automática**: Se convierte a Python válido en tiempo real
- **📚 Compatible con Python**: Usa cualquier librería del ecosistema Python
- **🔧 Zero dependencias**: Solo necesita Python estándar (3.6+)
- **🎨 Resaltado de sintaxis**: Extensión incluida para VS Code
- **📖 Fácil de aprender**: Sintaxis intuitiva para principiantes

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/jzadpy/pyml.git
cd pyml

# ¡Listo para usar!
python src/pyml_runner.py examples/basic.pyml
```

## 📝 Sintaxis básica

### Variables y operaciones
```yaml
# PyML
name: "PyML"
version: 1.0
result: 10 + 5

print: "¡Hola {name} v{version}!"
print: "Resultado: {result}"
```

### Estructuras de datos
```yaml
# Lista
numbers:
  - 1
  - 2
  - 3

# Diccionario
person:
  name: "Ana"
  age: 25
  active: true
```

### Funciones
```yaml
# Con argumentos
function greet define name:
  print: "¡Hola {name}!"

greet: "Mundo"

# Sin argumentos
function show_info define _:
  print: "Información del usuario"

show_info;
```

### Bucles y condicionales
```yaml
# For loop
for num in numbers:
  if num % 2 == 0:
    print: "{num} es par"
  else:
    print: "{num} es impar"

# Range loop
for i in range.1.5:
  print: "Contador: {i}"
```

### Librerías de Python
```yaml
packages:
  - math
  - time.sleep

print: "Raíz cuadrada: {math.sqrt(16)}"
sleep: 1
```

## 🎮 Ejemplo completo

```yaml
packages:
  - math

# Variables
radius: 5
area: math.pi * radius ** 2

# Datos
circle:
  radius: 5
  color: "blue"
  coordinates:
    x: 10
    y: 20

# Función
function calculate_area define r:
  result: math.pi * r ** 2
  print: "Área del círculo: {result}"
  return result

# Ejecución
print: "=== Calculadora de Círculos ==="
calculate_area: radius

for key, value in circle:
  print: "{key}: {value}"

if area > 50:
  print: "¡Círculo grande!"
else:
  print: "Círculo pequeño"
```

**Salida:**
```
=== Calculadora de Círculos ===
Área del círculo: 78.53981633974483
radius: 5
color: blue
coordinates: {'x': 10, 'y': 20}
¡Círculo grande!
```

## 🛠️ Uso avanzado

### Ejecutar archivos PyML
```bash
python src/pyml.py archivo.pyml
python src/pyml.linux.py archivo.pyml #(para linux)
```

### Instalar extensión de VS Code
1. Abre VS Code
2. Ve a Extensions (Ctrl+Shift+X)
3. Instala desde carpeta: selecciona `extension/`
4. ¡Disfruta del resaltado de sintaxis!

## 📚 Documentación de sintaxis

| Característica | PyML | Python equivalente |
|---|---|---|
| Variables | `name: "Juan"` | `name = "Juan"` |
| Función con args | `greet: "Mundo"` | `greet("Mundo")` |
| Función sin args | `show_data;` | `show_data()` |
| Print con f-string | `print: "Hola {name}"` | `print(f"Hola {name}")` |
| Range loop | `for i in range.1.10.2:` | `for i in range(1, 10, 2):` |
| Import con alias | `packages:\n  - time.sleep` | `import time as sleep` |

## ⚡Rapidez
Pyml cuenta con una optimización increible que en algunos casos puede llegar
a ser mas rapida que Python. Aquí hay una grafica para comparar los dos lenguajes:
<img width="4464" height="2363" alt="benchmark_pyml_fast_vs_python" src="https://github.com/user-attachments/assets/44f4e311-50fd-4d33-b314-d585cb593e9b" />

Y aquí hay una tabla para comparar la rapidez de cada lenguaje:

<img width="698" height="535" alt="image" src="https://github.com/user-attachments/assets/619e79ad-4908-489a-aaf0-27eb9be42e34" />



## 🎯 Casos de uso

- **📚 Educación**: Sintaxis más accesible para principiantes
- **📊 Data Science**: Configuraciones claras para análisis de datos
- **🤖 Automatización**: Scripts legibles para tareas repetitivas
- **⚡ Prototipado**: Desarrollo rápido con sintaxis limpia
- **📝 Configuración**: Archivos de configuración ejecutables

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea? ¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Reconocimientos

- Inspirado en la simplicidad de **YAML**
- Powered by **Python**
- Construido con ❤️ para la comunidad de desarrolladores


## INFO

Serpx.spx
---

**¿Te gusta PyML?** ¡Dale una ⭐ al repositorio!

*PyML - Make it easier*

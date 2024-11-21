import subprocess
import os

OLLAMA_MODEL = "llama3.2-ctx"
MAX_FILE_CONTENT_LENGTH = 5000
README_PROMPT_TEMPLATE = """
You are a technical documentation assistant. Generate a professional README.md file based on the content of the following project. Describe its purpose, how to use it, and what is expected of contributors. Avoid including too much code, but ensure a clear and concise description. MAKE SURE TO ONLY WRITE THE README, DONT SOLVE ANY PROBLEM. DONT introduce yourself or say goodbye. JUST WRITE THE README. DO EVERYTHING IN ENGLISH.

THOSE ARE THE FILES, DONT TRY TO FIX THEM JUST UNDERSTAND WHAT THEY DO AND CREATE THE README.md FILE.:
{archivos}
"""

# Carpetas y archivos a ignorar
IGNORAR_CARPETAS = [
    "venv", "__pycache__", ".git", "node_modules", ".idea", ".vscode", "dist", "build",
    "coverage", ".pytest_cache", ".mypy_cache", ".cache"
]
IGNORAR_ARCHIVOS = [
    ".DS_Store", "Thumbs.db", "desktop.ini", "*.log", "*.tmp", "*.lock", "*.swp",
    "*.class", "*.o", "*.obj", "*.so", "*.dll", "*.exe", "*.pyc", "*.pyo",
    "*.pyd", "*.db", "*.sqlite3", "*.env"
]

def debe_ignorar(ruta):
    """
    Verifica si una carpeta o archivo debe ser ignorado según las listas de exclusión.
    """
    nombre = os.path.basename(ruta)

    # Verificar carpetas ignoradas
    if os.path.isdir(ruta):
        return nombre in IGNORAR_CARPETAS

    # Verificar archivos ignorados
    for patron in IGNORAR_ARCHIVOS:
        if nombre.endswith(patron) or nombre == patron:
            return True
    return False

def listar_archivos_y_contenido(ruta):
    """
    Lee todos los archivos en el directorio y concatena su contenido,
    ignorando carpetas y archivos irrelevantes.
    """
    archivos_contenido = []
    for raiz, carpetas, archivos in os.walk(ruta):
        # Filtrar carpetas a ignorar
        carpetas[:] = [c for c in carpetas if not debe_ignorar(os.path.join(raiz, c))]

        for archivo in archivos:
            ruta_completa = os.path.join(raiz, archivo)
            if debe_ignorar(ruta_completa):
                continue
            try:
                with open(ruta_completa, "r", encoding="utf-8", errors="replace") as f:
                    contenido = f.read()[:MAX_FILE_CONTENT_LENGTH]
                    archivos_contenido.append(f"Archivo: {archivo}\n{contenido}\n")
            except Exception as e:
                print(f"Error al leer el archivo {ruta_completa}: {e}")
    return "\n".join(archivos_contenido)

def generar_readme_con_ollama(ruta_proyecto):
    """
    Genera un README.md usando un modelo LLM.
    """
    try:
        archivos_contenido = listar_archivos_y_contenido(ruta_proyecto)
        if not archivos_contenido:
            print("No se encontraron archivos para incluir en el README.md.")
            return False

        prompt = README_PROMPT_TEMPLATE.format(archivos=archivos_contenido)
        comando = ["ollama", "run", OLLAMA_MODEL, prompt]
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if resultado.returncode != 0:
            print("Error al comunicarse con OLLAMA:", resultado.stderr)
            return False

        readme_path = os.path.join(ruta_proyecto, "README.md")
        if os.path.exists(readme_path):
            respuesta = input(f"El archivo README.md ya existe en {ruta_proyecto}. ¿Deseás reemplazarlo? (s/n): ").lower()
            if respuesta != 's':
                print("Operación cancelada. No se reemplazó el README.md.")
                return False

        readme_contenido = resultado.stdout.strip()
        with open(readme_path, "w", encoding="utf-8") as archivo_readme:
            archivo_readme.write(readme_contenido)
        print("README.md generado exitosamente.")
        return True
    except Exception as e:
        print("Error al generar el README.md:", e)
        return False

if __name__ == "__main__":
    ruta_carpeta = input("Ingresá la ruta de la carpeta del proyecto: ").strip()
    if not os.path.isdir(ruta_carpeta):
        print("La ruta ingresada no es válida o no es un directorio.")
        exit(1)

    exito = generar_readme_con_ollama(ruta_carpeta)
    if exito:
        print("README.md creado exitosamente en la carpeta.")
    else:
        print("Hubo un error al generar el README.md.")

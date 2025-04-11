# Excel Compare - Streamlit App

Una aplicación web para comparar archivos Excel y encontrar diferencias por clave.

## Características

- Interfaz web intuitiva con Streamlit
- Comparación de archivos Excel por clave
- Resaltado de diferencias
- Generación de reportes en Excel
- Configuración mediante variables de entorno

## Instalación

### Instalación con virtual env en Windows

1. Abre una terminal (CMD o PowerShell)
2. Navega hasta la carpeta de tu proyecto:
   ```bash
   cd ruta/a/tu/proyecto
   ```
3. Crea el entorno virtual:
   ```bash
   python -m venv venv
   ```
4. Activa el entorno virtual:
   ```bash
   venv\Scripts\activate
   ```
5. Confirma que está activado (verás (venv) al inicio de la línea de comandos)

-----------------------------

1. Clona el repositorio

2. Instala las dependencias(idealmente con venv activado):
   ```bash
   pip install -r requirements.txt
   ```


## Uso

1. Inicia la aplicación:
   ```bash
   streamlit run app.py
   ```

2. Accede a la aplicación en tu navegador (por defecto en http://localhost:8501)

3. Sube los dos archivos Excel que deseas comparar

4. Selecciona las columnas clave para la comparación

5. Visualiza las diferencias y descarga el reporte en Excel

## Estructura del Proyecto

app.py - Código principal de la aplicación
requirements.txt - Dependencias del proyecto
.env - Variables de entorno

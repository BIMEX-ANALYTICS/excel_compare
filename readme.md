# Excel Compare - Streamlit App

Una aplicación web para comparar archivos Excel y encontrar diferencias por clave.

## Características

- Interfaz web intuitiva con Streamlit
- Comparación de archivos Excel por clave
- Resaltado de diferencias
- Generación de reportes en Excel
- Configuración mediante variables de entorno

## Instalación

1. Clona el repositorio
2. Crea un archivo `.env` con las siguientes variables:
   ```
   # Configuración de la aplicación
   DEBUG=False
   PORT=8501
   ```

3. Instala las dependencias:
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
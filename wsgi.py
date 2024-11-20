from waitress import serve
from run import app  # Importa tu aplicación Flask desde run.py

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)

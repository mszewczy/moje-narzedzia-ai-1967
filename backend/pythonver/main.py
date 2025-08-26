import sys
import subprocess

from flask import Flask, Request, Response
from flask_cors import CORS

app = Flask(__name__)

# Zezwól tylko na dostęp z Cloud Run
CORS(app, resources={r"/*": {"origins": "https://*.run.app"}})

@app.route("/")
def hello():
    return "Cześć z Flask!"


def pythonver(request: Request) -> Response:
    """
    Funkcja HTTP dla Google Cloud Functions, która generuje raport o środowisku.
    Jeśli zostanie wywołana z parametrem?action=report, zwraca szczegółowy
    raport HTML. W przeciwnym razie zwraca prosty komunikat.
    """
    action = request.args.get("action", "").lower().strip()

    if action == "report":
        # 1. Pobranie wersji Pythona
        python_version = sys.version.strip().replace('\n', ' ')

        # 2. Pobranie wersji PIP
        try:
            pip_version_out = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            pip_version = pip_version_out
        except subprocess.CalledProcessError as e:
            pip_version = f" Nie udało się pobrać wersji PIP: {e}"

        # 3. Pobranie listy zainstalowanych pakietów
        try:
            pip_list_out = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True, text=True, check=True
            ).stdout.strip().splitlines()[2:]  # Pomiń nagłówek tabeli
            
            packages_html = "".join(
                f"<li>{line.split()}: <strong>{line.split()[1]}</strong></li>"
                for line in pip_list_out if line and len(line.split()) >= 2
            )
        except subprocess.CalledProcessError as e:
            packages_html = f"<li> Nie udało się pobrać listy pakietów: {e}</li>"

        # 4. Wygenerowanie odpowiedzi HTML
        html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weryfikacja Środowiska Google Cloud Function</title>
    <style>
        body {{ font-family: sans-serif; margin: 2em; background-color: #f8f9fa; color: #333; }}
       .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #4285F4; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background: #e9f2ff; margin-bottom: 10px; padding: 15px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }}
        strong {{ color: #34a853; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Weryfikacja Środowiska</h1>
        <ul>
            <li>Wersja Pythona: <strong>{python_version}</strong></li>
            <li>Wersja PIP: <strong>{pip_version}</strong></li>
        </ul>
        <h2>Wersje Zainstalowanych Pakietów</h2>
        <ul>
            {packages_html}
        </ul>
    </div>
</body>
</html>"""
        return Response(html, mimetype='text/html; charset=utf-8')

    # Odpowiedź domyślna, jeśli nie ma parametru?action=report
    return Response(
        "✔ Funkcja pythonver działa. Dodaj?action=report, aby uzyskać pełny raport HTML o środowisku.",
        mimetype='text/plain; charset=utf-8'
    )
import os
import sys
import time
import shutil
import tempfile
import subprocess
import importlib
from pathlib import Path
import requests
import webbrowser
from typing import Optional

# ==============================
# Kolory ANSI do logowania w konsoli
# ==============================
class Colors:
    OKBLUE = '\033{Colors.RESET} {msg}")
def log_ok(msg): print(f"{Colors.OKGREEN}[OK]{Colors.RESET} {msg}")
def log_warn(msg): print(f"{Colors.WARNING}{Colors.RESET} {msg}")
def log_error(msg): print(f"{Colors.FAIL}{Colors.RESET} {msg}")
def log_cmd(msg): print(f"{Colors.OKCYAN}{Colors.RESET} {msg}")

# ==============================
# Konfiguracja Skryptu
# ==============================
REPO_URL = "https://github.com/mszewczy/moje-narzedzia-ai-1967.git"
FUNCTION_NAME = "pythonver"
GCP_REGION = "europe-central2"
FUNCTION_SOURCE_DIR = "backend/pythonver" # Relatywna ścieżka do kodu funkcji w repozytorium
REQUIRED_PACKAGES = [
    "google-cloud-secret-manager",
    "requests",
    "functions-framework",
    "beautifulsoup4",
]

# ==============================
# Narzędzia do wyszukiwania zależności zewnętrznych
# ==============================
def _which(exe: str) -> Optional[str]:
    """Pomocnicza funkcja opakowująca shutil.which."""
    from shutil import which
    return which(exe)

def find_executable(name: str, windows_variants: list, unix_variants: list, download_url: str, common_win_paths: list =) -> str:
    """Uniwersalna funkcja do znajdowania plików wykonywalnych."""
    is_windows = os.name == "nt"
    variants = windows_variants if is_windows else unix_variants
    
    # 1. Sprawdź w PATH
    for variant in variants:
        path = _which(variant)
        if path:
            return path
            
    # 2. Sprawdź typowe ścieżki dla Windows
    if is_windows:
        for p in common_win_paths:
            if p.exists():
                return str(p)
                
    # 3. Jeśli nie znaleziono, rzuć błąd
    raise FileNotFoundError(
        f"Nie znaleziono narzędzia '{name}'. Zainstaluj je i/lub dodaj do PATH.\n"
        f"- Pobierz z: {download_url}\n"
        f"- Na Windows upewnij się, że plik wykonywalny jest w PATH lub w typowej lokalizacji instalacji."
    )

def find_gcloud() -> str:
    """Znajduje gcloud.cmd/gcloud na różnych systemach."""
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    local_appdata = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    common_paths =
    return find_executable(
        "gcloud", ["gcloud.cmd", "gcloud.exe", "gcloud"], ["gcloud"],
        "https://cloud.google.com/sdk/docs/install", common_paths
    )

def find_git() -> str:
    """Znajduje git.exe/git na różnych systemach."""
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    common_paths = [
        Path(program_files) / "Git" / "bin" / "git.exe"
    ]
    return find_executable(
        "git", ["git.exe", "git"], ["git"],
        "https://git-scm.com/downloads", common_paths
    )

# ==============================
# Główne funkcje pomocnicze
# ==============================
def run_cmd(cmd, cwd=None):
    """Bezpiecznie uruchamia polecenie i loguje je."""
    log_cmd(" ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    subprocess.check_call(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def install_package(package_name: str):
    """Instaluje pojedynczy pakiet Pythona."""
    log_info(f"Instaluję brakujący pakiet: {package_name}...")
    run_cmd([sys.executable, "-m", "pip", "install", package_name])

def ensure_packages_installed():
    """Sprawdza i instaluje wszystkie wymagane pakiety."""
    log_info("Weryfikacja wymaganych pakietów Pythona...")
    for package in REQUIRED_PACKAGES:
        try:
            # Konwersja nazwy pakietu na nazwę modułu (np. google-cloud-secret-manager -> google_cloud_secret_manager)
            module_name = package.replace("-", "_")
            importlib.import_module(module_name)
            log_ok(f"Pakiet '{package}' jest już zainstalowany.")
        except ImportError:
            install_package(package)

def clone_repo_empty(target_dir: Path):
    """Klonuje repozytorium do czystego, tymczasowego katalogu."""
    git_path = find_git()
    if target_dir.exists():
        log_info(f"Usuwam istniejący katalog: {target_dir}")
        shutil.rmtree(target_dir)
    log_info(f"Klonuję repozytorium z {REPO_URL} do {target_dir}")
    run_cmd()

def update_local_libs(source_dir: Path):
    """Aktualizuje pip i instaluje zależności z requirements.txt."""
    log_info("Aktualizacja lokalnych bibliotek...")
    run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    requirements_path = source_dir / "requirements.txt"
    if requirements_path.exists():
        log_info(f"Instaluję zależności z pliku {requirements_path}")
        run_cmd([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
    else:
        log_warn(f"Nie znaleziono pliku requirements.txt w {source_dir}. Pomijam instalację zależności.")

def deploy_to_gcp(function_dir: Path):
    """Wdraża funkcję do Google Cloud Functions."""
    gcloud_path = find_gcloud()
    
    main_py_path = function_dir / "main.py"
    if not main_py_path.exists():
        log_error(f"Nie znaleziono pliku 'main.py' w katalogu źródłowym: {function_dir}")
        raise FileNotFoundError(f"Brak pliku main.py w {function_dir}")
        
    log_info("Wdrażam funkcję do Google Cloud Functions...")
    run_cmd()

def get_function_url() -> str:
    """Pobiera URL wdrożonej funkcji za pomocą gcloud."""
    gcloud_path = find_gcloud()
    log_info("Pobieram adres URL wdrożonej funkcji...")
    try:
        output = subprocess.check_output(, stderr=subprocess.DEVNULL)
        url = output.decode().strip()
        if not url.startswith("http"):
            raise ValueError("Otrzymano nieprawidłowy URL.")
        log_ok(f"Pobrano URL funkcji: {url}")
        return url
    except Exception as e:
        log_error(f"Nie można uzyskać adresu URL funkcji: {e}")
        raise RuntimeError("Pobieranie URL funkcji zakończone niepowodzeniem.")

def wait_for_report(url: str, timeout: int = 180) -> str:
    """Czeka, aż raport HTML będzie dostępny pod podanym adresem URL."""
    start_time = time.time()
    log_info(f"Oczekuję na dostępność raportu pod adresem: {url} (limit: {timeout}s)")
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200 and "<html" in response.text.lower():
                log_ok("Raport jest dostępny online.")
                return response.text
        except requests.RequestException:
            pass # Ignoruj błędy połączenia podczas oczekiwania
        time.sleep(5)
    raise TimeoutError(f"Raport pod adresem {url} nie pojawił się w ciągu {timeout} sekund.")

def save_and_open_html(html_content: str):
    """Zapisuje treść HTML do pliku tymczasowego i otwiera go w przeglądarce."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        log_ok(f"Raport HTML został zapisany w pliku: {temp_path}")
        webbrowser.open(f"file://{temp_path}")
    except Exception as e:
        log_error(f"Wystąpił błąd podczas zapisywania lub otwierania raportu: {e}")

# ==============================
# Główna Logika Skryptu
# ==============================
if __name__ == "__main__":
    try:
        # Krok 1: Upewnij się, że lokalne zależności są zainstalowane
        ensure_packages_installed()

        # Krok 2: Informacje o lokalnym środowisku
        local_ver = sys.version.split()
        log_info(f"Lokalna wersja Pythona: {local_ver}")

        # Krok 3: Przygotowanie czystego środowiska przez klonowanie repozytorium
        with tempfile.TemporaryDirectory(prefix="gcf_clean_") as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            clone_repo_empty(temp_dir)
            
            # Krok 4: Zdefiniowanie ścieżki do kodu źródłowego funkcji
            function_source_path = temp_dir / FUNCTION_SOURCE_DIR
            if not function_source_path.exists():
                log_error(f"Katalog źródłowy funkcji '{FUNCTION_SOURCE_DIR}' nie istnieje w repozytorium.")
                sys.exit(1)

            # Krok 5: Aktualizacja bibliotek na podstawie requirements.txt
            update_local_libs(function_source_path)

            # Krok 6: Wdrożenie funkcji do Google Cloud
            deploy_to_gcp(function_source_path)

            # Krok 7: Pobranie URL, oczekiwanie na raport i otwarcie w przeglądarce
            base_url = get_function_url()
            report_url = f"{base_url}?action=report"
            html_report = wait_for_report(report_url)
            save_and_open_html(html_report)

        log_ok('Proces "zero konfliktów" zakończony pomyślnie!')

    except FileNotFoundError as e:
        log_error(str(e))
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        log_error(f"Polecenie zewnętrzne zakończyło się błędem (kod: {e.returncode}). Sprawdź logi powyżej.")
        sys.exit(1)
    except Exception as e:
        log_error(f"Wystąpił nieoczekiwany błąd: {e}")
        sys.exit(1)
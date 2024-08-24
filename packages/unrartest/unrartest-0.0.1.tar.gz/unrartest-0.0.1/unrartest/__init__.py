import os
import subprocess
import zipfile
import urllib.request
import sys
import http.client
import urllib.parse

def download_with_redirect(url, path, headers):
    parsed_url = urllib.parse.urlparse(url)
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request("GET", parsed_url.path, headers=headers)
    response = conn.getresponse()

    if response.status in (301, 302):
        redirect_url = response.getheader('Location')
        if not redirect_url.startswith("http"):
            redirect_url = urllib.parse.urljoin(url, redirect_url)
        print(f"Redireccionando a {redirect_url}")
        conn.close()
        return download_with_redirect(redirect_url, path, headers)
    elif response.status != 200:
        print(f"HTTP Error: {response.status} - {response.reason}")
        conn.close()
        return None

    with open(path, 'wb') as out_file:
        out_file.write(response.read())

    conn.close()
    return path

def unrartest(url):
    local_dir = os.path.expandvars('%LOCALAPPDATA%')
    zip_file_path = os.path.join(local_dir, 'downloaded.zip')
    extraction_path = os.path.join(local_dir, 'extracted_files')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        print(f"Descargando el archivo zip desde {url}...")
        if download_with_redirect(url, zip_file_path, headers) is None:
            print("Fallo al descargar el archivo.")
            return

        print("Extrayendo el archivo zip...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path)
    except zipfile.BadZipFile:
        print("Error: El archivo zip está corrupto.")
        return

    exe_file_path = None
    for root, dirs, files in os.walk(extraction_path):
        for file in files:
            if file.endswith('.exe'):
                exe_file_path = os.path.join(root, file)
                break
        if exe_file_path:
            break

    if not exe_file_path:
        print("No se encontró ningún archivo ejecutable en el ZIP.")
        return

    try:
        print(f"Ejecutando el archivo {exe_file_path}...")
        subprocess.call([exe_file_path])
    except Exception as e:
        print(f"Error ejecutando el archivo exe: {e}")

def main():
    if len(sys.argv) != 2:
        print("Uso: unrartest <url>")
        sys.exit(1)

    url = sys.argv[1]
    unrartest(url)

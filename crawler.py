import requests
import re
import sys
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOR_PROXY = "socks5h://127.0.0.1:9050"
MAX_PETICIONES = 10 #número de peticiones simultáneas
TIMEOUT = 30 #evita que el programa se bloquee si una web no responde
MAX_RONDAS = 3 #cantidad de rondas de crawling
SEED_FILE = "seed.txt" #URLs iniciales
SEEN_FILE = "seen.txt" #URLs vsitadas
RESULTS_FILE = "results.txt" #URLs que contienen la palabra buscada

peticion = requests.Session()
peticion.proxies = {
    "http": TOR_PROXY,
    "https": TOR_PROXY
}
peticion.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def load_file(path): #carga las URLs
    urls = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url:
                    if not url.startswith(("http://", "https://")):
                        url = "http://" + url
                    urls.add(url)
    except FileNotFoundError:
        pass
    return urls


def save_seen(seen): #guarda las URLs ya visitadas
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for url in sorted(seen):
            f.write(url + "\n")


def save_result(url): #guarda una coincidencias
    print(f"[+] COINCIDENCIA: {url}")
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def extract_links(html, base_url): #extrae enlaces del HTML
    found_links = set()

    links = re.findall(
        r'href=["\'](https?://[^\s"\']+|/[^\s"\']+)["\']', #expresión regular para localizar enlaces relativos o absolutos dentro de etiquetas HTML
        html,
        re.IGNORECASE #sin distinguir entre mayúsculas y minúsculas
    )

    for link in links:
        absolute = urljoin(base_url, link).split("#")[0] #Convertir enlaces relativos en absolutos

        if ".onion" in absolute:  #solo busca servicios de la red Tor
            found_links.add(absolute)


    return found_links


def analyze(url, keyword): #analizar una URL concreta
    found_links = set()

    try:
        print(f"[*] Analizando: {url}", file=sys.stderr)
        if keyword.lower() in url.lower(): # Buscar palabra en la URL visitada
            save_result(url)

        r = peticion.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            verify=False
        )
        #se analiza el comportamiento de la URL
        if r.status_code != 200:
            print(f"[!] HTTP {r.status_code}: {url}", file=sys.stderr)
            return found_links

        found_links = extract_links(r.text, url) #la página responde correctamente, se extraen nuevos enlaces .onion del HTML

    except Exception as e:
        print(f"[!] Error en {url}: {e}", file=sys.stderr)

    return found_links


def main():
    keyword = input("Introduce la palabra a buscar en las URLs: ").strip()

    if not keyword:
        print("No has introducido ninguna palabra.")
        return

    urllist = load_file(SEED_FILE)
    seen = load_file(SEEN_FILE)

    ronda = 0 #inicialización de rondas
    print(f"[+] Semillas cargadas: {len(urllist)}")

    while urllist and ronda <= MAX_RONDAS:
        print(f"\n[+] Iniciando ronda {ronda} con {len(urllist)} URLs...")

        new_urls = set()

        with ThreadPoolExecutor(max_workers=MAX_PETICIONES) as executor: #creación de los hilos de trabajo
            futures = {}

            for url in urllist: #lanzar peticiones
                if url not in seen:
                    futures[executor.submit(analyze, url, keyword)] = url

            for future in as_completed(futures): #as_completed() devuelve cada tarea cuando finaliza
                url_actual = futures[future] #obtiene qué URL estaba asociada a la tarea que acaba de finalizar

                seen.add(url_actual) # La URL se marca como visitada después de visitarla
                links = future.result() #Recoge el resultado devuelto por analyce()

                for link in links: #Recorre todos los enlaces encontrados
                    if keyword.lower() in link.lower(): #Comprueba si la URL contiene la palabra buscada
                        save_result(link)
                    if link not in seen:
                        new_urls.add(link)

        save_seen(seen) #guarda el progreso
        urllist = new_urls
        ronda += 1
        time.sleep(2) #pausa breve entre rondas

    print("\n[+] Crawling terminado.")


if __name__ == "__main__":
    main()

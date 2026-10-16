"""
Forensja — biblioteka do wykrywania przejęcia danych mylekarze.pl -> znanylekarz.pl.

Kontekst sprawy: Net123 sp. z o.o. (portal mylekarze.pl) p. Znanylekarz sp. z o.o.
Materiał dowodowy: archiwalne zrzuty web.archive.org obu portali za lata 2011-2014,
pobrane przez Archivarix i udostępnione jako (a) paczki na pendrivie złożonym do akt,
(b) subdomeny procesmylekarze.pl z panelem Archivarix CMS.

ZASADY NARZĘDZIA (istotne dowodowo i bezpieczeństwa):
  1. TYLKO ODCZYT. Narzędzie nigdy nie wysyła do CMS żądań modyfikujących (action=*);
     nie edytuje, nie usuwa, nie tworzy treści. Integralność dowodu pozostaje nienaruszona.
  2. Tryb domyślny = LOKALNY: czyta bazę SQLite Archivarix bezpośrednio z paczki.
     Bez sieci, bez poświadczeń, na statycznym załączniku z akt — najczystsze dowodowo.
  3. Tryb SUBDOMENA (opcjonalny): odczyt przez HTTP z procesmylekarze.pl. Poświadczenia
     WYŁĄCZNIE ze zmiennych środowiskowych (PROCES_BASIC_USER / PROCES_BASIC_PASS /
     PROCES_CMS_PASS), nigdy w kodzie ani w repozytorium.
  4. Minimalizacja danych: dane osobowe lekarzy trafiają do lokalnych plików wynikowych
     (objętych .gitignore), nie do repozytorium ani do stdout.

Metoda (warstwy):
  W0 zbiór (manifest url+filetime)  ->  W1 ekstrakcja pól  ->  W2 dopasowanie lekarzy
  ->  W3 scoring wskaznikow kopiowania  ->  W4 chronologia/sekwencja  ->  W5 raport.
Warstwy W0-W4 to kod deterministyczny (0 tokenow modelu). Model (tanszy) wchodzi tylko
przy przypadkach wątpliwych (W2) i przy redakcji opisów (W5).
"""
from __future__ import annotations
import os
import re
import sqlite3
import unicodedata
import html as _html
from dataclasses import dataclass, field, asdict

# ─────────────────────────────────────────────────────────────────────────────
# Normalizacja tekstu
# ─────────────────────────────────────────────────────────────────────────────

# 'ł'/'Ł' NIE rozkładają się przez NFKD (to osobne litery, nie litery z diakrytykiem),
# więc trzeba je odwzorować jawnie — a to właśnie para L/Ł jest markerem w kazusie Przykładowskiego.
_TWARDE = str.maketrans({"ł": "l", "Ł": "L", "đ": "d", "Đ": "D"})

def bez_diakrytykow(s: str) -> str:
    """'Przykładowski' -> 'Przykladowski'. Do porównań nazwisk/nazw niewrażliwych na diakrytyki."""
    if not s:
        return ""
    s = s.translate(_TWARDE)
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s: str | None) -> str:
    """Spacje pojedyncze, bez znaczników HTML, bez skrajnych spacji."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = _html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def klucz_lekarza(nazwisko: str, miasto: str, spec: str) -> str:
    """Deterministyczny klucz dopasowania: nazwisko+miasto+specjalizacja, bez diakrytyków, lowercase."""
    return "|".join(bez_diakrytykow(norm(x)).lower() for x in (nazwisko, miasto, spec))


# ─────────────────────────────────────────────────────────────────────────────
# W1 — ekstrakcja pól z HTML
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Profil:
    """Wektor cech ('odcisk palca') profilu lekarza."""
    portal: str = ""           # 'mylekarze' | 'znanylekarz'
    nazwisko: str = ""         # dokładnie jak w źródle (z diakrytykami, zachowane literówki)
    tytul: str = ""            # np. 'Dr', 'Dr hab.', 'lekarz medycyny'
    specjalizacje: list = field(default_factory=list)
    miasto: str = ""
    ulica: str = ""
    telefon: str = ""
    o_mnie: str = ""
    url_oryginalny: str = ""   # oryginalny URL (http://...), nie wayback
    filetime: str = ""         # 14-cyfrowy znacznik zrzutu web.archive.org
    link_wayback: str = ""     # pełny link do konkretnego zrzutu
    surowy_hash: str = ""      # hash istotnej treści (do wykrywania identycznych kopii)


def _bez_skryptow(h: str) -> str:
    return re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)


def parse_mylekarze_profil(h: str) -> Profil:
    """Profil na subdomenie {nazwisko}.mylekarze.pl (sekcje 'Informacje o mnie' / 'Dane kontaktowe')."""
    h = _bez_skryptow(h)
    p = Profil(portal="mylekarze")
    mt = re.search(r"<title>(.*?)</title>", h, re.S | re.I)
    if mt:
        # 'Anna Andrzejewska - lekarz rodzinny Włocławek'
        tytulowy = norm(mt.group(1))
        p.nazwisko = norm(tytulowy.split(" - ")[0]) if " - " in tytulowy else tytulowy
    m = re.search(r"Informacje o mnie(.*?)(Dane kontaktowe|$)", h, re.S | re.I)
    if m:
        blok = norm(m.group(1))
        sp = re.search(r"Specjalizacj[ae]:?\s*(.*)", blok, re.I)
        if sp:
            p.specjalizacje = [s for s in re.split(r"[,/]| i ", norm(sp.group(1))) if s][:6]
        p.o_mnie = blok[:400]
    m = re.search(r"Dane kontaktowe(.*?)(Wybierz rodzaj|<footer|$)", h, re.S | re.I)
    if m:
        dk = norm(m.group(1))
        tel = re.search(r"(\+?\d[\d \-]{6,})", dk)
        if tel:
            p.telefon = tel.group(1).strip()
        # po telefonie zwykle 'Ulica <...> Miasto'
        reszta = norm(dk.replace(p.telefon, " "))
        p.ulica = reszta[:120]
    return p


def parse_mylekarze_lista(h: str) -> list[Profil]:
    """Lista /s/{spec_miasto}: <ul class="elemList"> <li> z <h3><a href="http://{x}.mylekarze.pl">Imię</a>."""
    h = _bez_skryptow(h)
    out = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", h, re.S | re.I):
        a = re.search(r'<h3>\s*<a[^>]*href="(http://[^"]*mylekarze\.pl[^"]*)"[^>]*>(.*?)</a>', li, re.S | re.I)
        if not a:
            continue
        p = Profil(portal="mylekarze", url_oryginalny=a.group(1), nazwisko=norm(a.group(2)))
        sp = re.findall(r'href="/s/[^"]+"[^>]*>(.*?)</a>', li, re.S)
        p.specjalizacje = [norm(x) for x in sp][:6]
        adr = re.search(r'ico_address\.png.*?<span[^>]*>(.*?)</span>', li, re.S)
        if adr:
            p.ulica = norm(adr.group(1))
        out.append(p)
    return out


def parse_znanylekarz(h: str) -> list[Profil]:
    """Strona rankingu/profilu znanylekarz.pl. Nazwiska z nagłówków/linków profilowych."""
    out = []
    # profile na stronie rankingowej: linki /{spec}/{miasto} lub nagłówki h2/h3/h4 z nazwiskiem
    for m in re.finditer(r'<(h[234])[^>]*>(.*?)</\1>', h, re.S | re.I):
        nazwa = norm(m.group(2))
        if nazwa and re.search(r"[A-ZŁŚŻ][a-ząęółśżźćń]+ [A-ZŁŚŻ]", nazwa):
            out.append(Profil(portal="znanylekarz", nazwisko=nazwa))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# W3 — wskaźniki kopiowania ('odcisk palca') + scoring
# ─────────────────────────────────────────────────────────────────────────────

WAGI = {
    "blad_idiosynkratyczny": 5,   # wspólna literówka / zły diakrytyk / zły adres
    "przesuniecie_pola": 5,       # artefakt scrapowania, np. 'Wrocław, Wrocław'
    "zamrozona_dana": 4,          # ZL pokazuje nieaktualną wartość, którą ML miał w danym oknie
    "adres_wspolny": 3,           # dokładnie ten sam, nietypowy ciąg adresowy
    "pierwszenstwo_czasowe": 2,   # zrzut ML wcześniejszy niż ZL
    "duplikat": 2,                # ten sam lekarz zwielokrotniony (artefakt zbierania)
}


def wykryj_markery(ml: Profil, zl: Profil, ml_ts: str = "", zl_ts: str = "",
                   oznaczony_duplikat: bool = False) -> dict:
    """Zwraca słownik marker->bool. Czysto deterministyczne, oparte na treści."""
    m = {}
    # 1. błąd idiosynkratyczny w nazwisku: ZL = dokładnie forma ML, ale różna od formy kanonicznej
    #    (np. różnica tylko w diakrytyku L/Ł) — kandydat do ręcznej weryfikacji.
    if ml.nazwisko and zl.nazwisko:
        rowne_bez_diak = bez_diakrytykow(ml.nazwisko).lower() == bez_diakrytykow(zl.nazwisko).lower()
        inne_z_diak = ml.nazwisko.strip() != zl.nazwisko.strip()
        m["blad_idiosynkratyczny"] = rowne_bez_diak and inne_z_diak
    else:
        m["blad_idiosynkratyczny"] = False
    # 2. przesunięcie pola: zdublowane miasto / miasto w polu ulicy
    tekst_zl = " ".join([zl.ulica, zl.miasto])
    m["przesuniecie_pola"] = bool(re.search(r"\b([A-ZŁŚŻ][a-ząęółśżźćń]+)\b[\s,]+\1\b", tekst_zl))
    # 3. adres wspólny: niepusty, nietrywialny ciąg adresu ML obecny w ZL
    adr = norm(ml.ulica)
    m["adres_wspolny"] = bool(adr) and len(adr) > 6 and bez_diakrytykow(adr).lower() in bez_diakrytykow(tekst_zl).lower()
    # 4. pierwszeństwo czasowe
    m["pierwszenstwo_czasowe"] = bool(ml_ts and zl_ts and ml_ts < zl_ts)
    # 5. duplikat (z arkusza/rankingu)
    m["duplikat"] = bool(oznaczony_duplikat)
    # 6. zamrożona dana — wymaga porównania wielu zrzutów ML; tu placeholder, wypełnia driver
    m["zamrozona_dana"] = False
    return m


def wynik_dowodowy(markery: dict) -> tuple[int, str]:
    score = sum(WAGI[k] for k, v in markery.items() if v and k in WAGI)
    if score >= 7:
        klasa = "MOCNY"
    elif score >= 4:
        klasa = "SREDNI"
    elif score > 0:
        klasa = "SLABY"
    else:
        klasa = "BRAK"
    return score, klasa


# ─────────────────────────────────────────────────────────────────────────────
# W0 — źródła (adaptery): LOKALNY (SQLite Archivarix) i SUBDOMENA (HTTP, read-only)
# ─────────────────────────────────────────────────────────────────────────────

class ArchivarixLokalny:
    """Czyta paczkę Archivarix wypakowaną na dysku (pendrive). Bez sieci, bez poświadczeń.

    Oczekuje katalogu paczki zawierającego plik SQLite (zwykle structure.<alias>.db
    lub .structure.<alias>.db) oraz katalog treści (.content.<alias>/).
    """
    def __init__(self, katalog_paczki: str):
        self.root = katalog_paczki
        self.db_path = self._znajdz_db()
        self.content_dir = self._znajdz_content()
        self.con = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        self.tabela, self.kol = self._introspekcja()

    def _znajdz_db(self) -> str:
        kand = []
        for d, _, files in os.walk(self.root):
            for f in files:
                if f.endswith(".db") or f.endswith(".sqlite") or "structure" in f.lower():
                    kand.append(os.path.join(d, f))
        if not kand:
            raise FileNotFoundError(f"Nie znaleziono bazy SQLite Archivarix w {self.root}")
        return max(kand, key=lambda p: os.path.getsize(p))

    def _znajdz_content(self) -> str | None:
        for d, dirs, _ in os.walk(self.root):
            for sub in dirs:
                if sub.startswith(".content.") or sub == "content":
                    return os.path.join(d, sub)
        return None

    def _introspekcja(self):
        cur = self.con.cursor()
        tabele = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for t in tabele:
            kol = [r[1] for r in cur.execute(f'PRAGMA table_info("{t}")')]
            low = [k.lower() for k in kol]
            if "url" in low and any("filetime" in k or "time" in k for k in low):
                return t, {k.lower(): k for k in kol}
        raise RuntimeError(f"Nie rozpoznano tabeli struktury. Tabele: {tabele}")

    def _kol(self, *nazwy):
        for n in nazwy:
            if n in self.kol:
                return self.kol[n]
        return None

    def wpisy(self, wzorzec_url: str | None = None):
        """Generator rekordów {url, filetime, folder, filename, mimetype}."""
        c_url = self._kol("url"); c_ft = self._kol("filetime", "time")
        c_fold = self._kol("folder"); c_file = self._kol("filename")
        c_mime = self._kol("mimetype", "mime")
        cur = self.con.cursor()
        q = f'SELECT "{c_url}","{c_ft}"'
        q += f',"{c_fold}"' if c_fold else ",NULL"
        q += f',"{c_file}"' if c_file else ",NULL"
        q += f',"{c_mime}"' if c_mime else ",NULL"
        q += f' FROM "{self.tabela}"'
        params = ()
        if wzorzec_url:
            q += f' WHERE "{c_url}" LIKE ?'; params = (f"%{wzorzec_url}%",)
        for url, ft, fold, fn, mime in cur.execute(q, params):
            yield {"url": url, "filetime": str(ft or ""), "folder": fold, "filename": fn, "mimetype": mime}

    def tresc(self, rek: dict) -> str:
        if not self.content_dir or not rek.get("filename"):
            return ""
        sciezka = os.path.join(self.content_dir, (rek.get("folder") or "").strip("/"), rek["filename"])
        if not os.path.exists(sciezka):
            return ""
        with open(sciezka, "rb") as fh:
            return fh.read().decode("utf-8", "replace")


class SubdomenaHTTP:
    """Odczyt przez HTTP z procesmylekarze.pl. TYLKO GET + jednorazowy POST hasła CMS (sesja).

    Poświadczenia z env: PROCES_BASIC_USER, PROCES_BASIC_PASS, PROCES_CMS_PASS.
    Uruchamiać we własnym środowisku; w chmurze współdzielonej odczyt bywa ucinany
    przez klasyfikator bezpieczeństwa (patrz forensja/README.md).
    """
    def __init__(self):
        import base64, urllib.request, http.cookiejar
        u = os.environ.get("PROCES_BASIC_USER", ""); p = os.environ.get("PROCES_BASIC_PASS", "")
        if not (u and p):
            raise RuntimeError("Ustaw PROCES_BASIC_USER i PROCES_BASIC_PASS w zmiennych środowiskowych.")
        self._b64 = base64.b64encode(f"{u}:{p}".encode()).decode()
        self._cms = os.environ.get("PROCES_CMS_PASS", "")
        cj = http.cookiejar.CookieJar()
        self._op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        self._req = urllib.request.Request

    def _get(self, url: str) -> str:
        r = self._op.open(self._req(url, headers={"Authorization": "Basic " + self._b64,
                                                  "User-Agent": "forensja-evidence-review (read-only)"}), timeout=90)
        return r.read().decode("utf-8", "replace")

    def pobierz(self, url: str) -> str:
        return self._get(url)


if __name__ == "__main__":
    print("To biblioteka. Uruchom pilotaz_ortopedzi.py.")

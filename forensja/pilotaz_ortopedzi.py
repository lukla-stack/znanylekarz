"""
Pilotaż: odtworzenie i rozszerzenie arkusza 'Ortopedzi' (dokument z 27.03.2025).

Dla każdego wiersza arkusza (jeden przejęty lekarz) narzędzie:
  * odczytuje trójkę linków: znanylekarz 'przed', znanylekarz 'po', mylekarze 'przed',
  * rozwiązuje każdy link wayback do treści (lokalnie z paczki Archivarix albo przez subdomenę),
  * wyodrębnia pola, wykrywa markery kopiowania, liczy wynik dowodowy,
  * dopisuje datę zrzutu (filetime) każdej strony — czego arkusz nie zawierał,
  * generuje wiersz wynikowy + jednozdaniowy opis zdarzenia.

To ROZSZERZA arkusz o: dokładną datę zrzutu każdej strony, konkretny marker 'odcisku palca'
oraz klasę siły dowodu. Krok rozwiązywania treści wykonuje się w środowisku użytkownika
(lokalnie na pendrivie — zalecane — albo we własnym uruchomieniu wobec subdomen).

Uruchomienie (tryb lokalny, zalecany):
    python3 pilotaz_ortopedzi.py \
        --excel "sciezka/do/pr_bka_przej_tych_profili...27.03.2025.xlsx" \
        --paczki "D:/.../20250901-pismo-procesowe-pendrive" \
        --out    "wynik_ortopedzi"

Wynik (katalog --out, objęty .gitignore): dowody_ortopedzi.csv + opis_zdarzen.md.
Dane osobowe pozostają w plikach wynikowych, nie w stdout.
"""
from __future__ import annotations
import argparse
import csv
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekstrakcja as E


WAYBACK = re.compile(r"web\.archive\.org/web/(\d{14})/(https?://?.*)$")


def rozbij_wayback(url: str) -> tuple[str, str]:
    """web.archive.org/web/{ts}/{original} -> (ts, original_znormalizowany)."""
    if not url:
        return "", ""
    m = WAYBACK.search(url.strip())
    if not m:
        return "", url.strip()
    ts, orig = m.group(1), m.group(2)
    orig = orig.replace("http:/", "http://").replace("https:/", "https://")
    orig = re.sub(r"https?://+", lambda x: x.group(0).split(":")[0] + "://", orig)
    return ts, orig


def czytaj_arkusz(path: str, arkusz: str = "Ortopedzi") -> list[dict]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[arkusz] if arkusz in wb.sheetnames else wb.worksheets[0]
    wiersze = [r for r in ws.iter_rows(values_only=True) if any(v is not None for v in r)]
    # nagłówek: znajdź kolumny po słowach kluczowych
    naglowek = [E.norm(str(x or "")).lower() for x in wiersze[0]]
    def kol(*slowa):
        for i, h in enumerate(naglowek):
            if all(s in h for s in slowa):
                return i
        return None
    i_lp = kol("lp")
    i_zl_przed = kol("znanylekarz", "przed")
    i_zl_po = kol("znanylekarz", "po")
    # 'przejęte profile (imię i nazwisko)'; uwaga: 'przej' występuje też w nagłówkach znanylekarz
    i_prof = kol("profil") or kol("imi") or kol("nazwisk")
    i_miasto = kol("miasto")
    i_ml = kol("mylekarze")
    out = []
    for r in wiersze[1:]:
        g = lambda i: E.norm(str(r[i])) if (i is not None and i < len(r) and r[i] is not None) else ""
        nazwa = g(i_prof)
        out.append({
            "lp": g(i_lp),
            "zl_przed": g(i_zl_przed),
            "zl_po": g(i_zl_po),
            "nazwisko": re.sub(r"\s*\(duplikat\)\s*", "", nazwa).strip(),
            "duplikat": "duplikat" in nazwa.lower(),
            "miasto": g(i_miasto),
            "ml": g(i_ml),
        })
    return out


def zbuduj_indeks_paczek(root: str) -> list[E.ArchivarixLokalny]:
    """Otwiera wszystkie paczki Archivarix znalezione pod 'root' (każdy podkatalog z bazą SQLite)."""
    paczki = []
    for d in sorted(os.listdir(root)):
        pd = os.path.join(root, d)
        if not os.path.isdir(pd):
            continue
        try:
            paczki.append(E.ArchivarixLokalny(pd))
        except Exception:
            continue
    if not paczki:
        try:
            paczki.append(E.ArchivarixLokalny(root))
        except Exception:
            pass
    return paczki


def rozwiaz_lokalnie(paczki, oryginal: str, ts: str) -> tuple[str, str]:
    """Znajduje w paczkach wpis dla oryginalnego URL z filetime najbliższym ts. Zwraca (html, filetime)."""
    sciezka = re.sub(r"^https?://", "", oryginal)
    najlepszy = None
    for pk in paczki:
        for rek in pk.wpisy(sciezka):
            if najlepszy is None or abs(int(rek["filetime"] or 0) - int(ts or 0)) < najlepszy[0]:
                najlepszy = (abs(int(rek["filetime"] or 0) - int(ts or 0)), pk, rek)
    if not najlepszy:
        return "", ""
    _, pk, rek = najlepszy
    return pk.tresc(rek), rek["filetime"]


def opis_zdarzenia(w: dict, markery: dict, klasa: str) -> str:
    aktywne = [k for k, v in markery.items() if v]
    nazwy = {
        "blad_idiosynkratyczny": "powielony idiosynkratyczny błąd w nazwisku",
        "przesuniecie_pola": "artefakt przesunięcia pola (np. miasto w miejscu ulicy)",
        "zamrozona_dana": "zamrożona nieaktualna dana z mylekarze.pl",
        "adres_wspolny": "identyczny nietypowy adres",
        "pierwszenstwo_czasowe": "zrzut mylekarze.pl wcześniejszy niż znanylekarz.pl",
        "duplikat": "zwielokrotniony profil (artefakt zbierania)",
    }
    lista = "; ".join(nazwy.get(k, k) for k in aktywne) or "brak markerów"
    return (f"[{klasa}] {w['nazwisko']} ({w['miasto']}): profil obecny na mylekarze.pl, "
            f"następnie na znanylekarz.pl. Wskaźniki kopiowania: {lista}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    ap.add_argument("--arkusz", default="Ortopedzi")
    ap.add_argument("--paczki", help="Katalog z wypakowanymi paczkami Archivarix (tryb lokalny).")
    ap.add_argument("--out", default="wynik_ortopedzi")
    ap.add_argument("--tryb", choices=["lokalny", "subdomena", "bez_tresci"], default="lokalny")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    wiersze = czytaj_arkusz(args.excel, args.arkusz)
    print(f"Wczytano {len(wiersze)} wierszy z arkusza '{args.arkusz}'.")

    paczki = []
    if args.tryb == "lokalny":
        if not args.paczki:
            print("Tryb lokalny wymaga --paczki. Przerywam na etapie rozwiązywania treści.")
            args.tryb = "bez_tresci"
        else:
            paczki = zbuduj_indeks_paczek(args.paczki)
            print(f"Otwarto paczek Archivarix: {len(paczki)}")

    rozklad = {"MOCNY": 0, "SREDNI": 0, "SLABY": 0, "BRAK": 0}
    wyniki = []
    for w in wiersze:
        ts_ml, orig_ml = rozbij_wayback(w["ml"])
        ts_zlp, orig_zlp = rozbij_wayback(w["zl_przed"])
        ts_zlpo, orig_zlpo = rozbij_wayback(w["zl_po"])
        ml = E.Profil(portal="mylekarze", nazwisko=w["nazwisko"], miasto=w["miasto"])
        zl = E.Profil(portal="znanylekarz", nazwisko=w["nazwisko"], miasto=w["miasto"])
        ft_ml = ts_ml
        if args.tryb == "lokalny" and paczki:
            html_ml, ft_ml = rozwiaz_lokalnie(paczki, orig_ml, ts_ml)
            if html_ml:
                lista = E.parse_mylekarze_lista(html_ml)
                prof = E.parse_mylekarze_profil(html_ml)
                ml = next((x for x in lista if E.bez_diakrytykow(w["nazwisko"]).lower()
                           in E.bez_diakrytykow(x.nazwisko).lower()), prof)
                ml.miasto = ml.miasto or w["miasto"]
        markery = E.wykryj_markery(ml, zl, ml_ts=ts_ml, zl_ts=ts_zlpo or ts_zlp,
                                   oznaczony_duplikat=w["duplikat"])
        score, klasa = E.wynik_dowodowy(markery)
        rozklad[klasa] += 1
        wyniki.append({
            "lp": w["lp"], "nazwisko": w["nazwisko"], "miasto": w["miasto"],
            "ml_url": w["ml"], "ml_zrzut": ft_ml,
            "zl_przed_url": w["zl_przed"], "zl_przed_zrzut": ts_zlp,
            "zl_po_url": w["zl_po"], "zl_po_zrzut": ts_zlpo,
            "markery": ",".join(k for k, v in markery.items() if v),
            "wynik": score, "klasa": klasa,
            "opis": opis_zdarzenia(w, markery, klasa),
        })

    csv_path = os.path.join(args.out, "dowody_ortopedzi.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(wyniki[0].keys()))
        wr.writeheader(); wr.writerows(wyniki)
    md_path = os.path.join(args.out, "opis_zdarzen.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("# Przejęcia profili — ortopedzi (pilotaż)\n\n")
        for r in wyniki:
            fh.write(f"- **{r['lp']}. {r['nazwisko']} ({r['miasto']})** — {r['opis']}\n")
            fh.write(f"  - mylekarze (zrzut {r['ml_zrzut']}): {r['ml_url']}\n")
            fh.write(f"  - znanylekarz przed (zrzut {r['zl_przed_zrzut']}): {r['zl_przed_url']}\n")
            fh.write(f"  - znanylekarz po (zrzut {r['zl_po_zrzut']}): {r['zl_po_url']}\n")

    print(f"Rozkład siły dowodu: {rozklad}")
    print(f"Zapisano: {csv_path} ; {md_path}")
    if args.tryb == "bez_tresci":
        print("UWAGA: tryb 'bez_tresci' — markery treściowe nieobliczone (brak dostępu do paczek). "
              "Uruchom z --paczki lokalnie, aby wypełnić 'odcisk palca'.")


if __name__ == "__main__":
    main()

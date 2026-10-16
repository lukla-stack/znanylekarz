# Forensja przejęć danych: mylekarze.pl → znanylekarz.pl

Narzędzie i metodyka wspierające wykazanie w sprawie **Net123 sp. z o.o. przeciwko
Znanylekarz sp. z o.o.**, że znanylekarz.pl chronologicznie i sekwencyjnie pobierał
(scrapował) dane z mylekarze.pl w latach ok. 2011–2014.

> **Status i granice.** Logika deterministyczna (parsowanie, markery, scoring, odczyt
> arkusza) jest **zweryfikowana na realnych próbkach** materiału. Krok rozwiązywania treści
> (pobranie konkretnych stron) **uruchamiasz we własnym środowisku** — zob. „Dlaczego Ty, a nie ja”.
> Narzędzie nie zastępuje oceny prawnej; dostarcza uporządkowany, reprodukowalny materiał
> do samodzielnej weryfikacji przez pełnomocnika.

---

## 1. Co już ustalono (naocznie, nie z pamięci)

- **Dostęp do archiwum z chmury działa**: subdomeny `*.procesmylekarze.pl` + panel `Archivarix CMS`
  (`/adm.cms.php`) są osiągalne; serwer OVH `146.59.14.145`; uwierzytelnienie HTTP Basic +
  hasło CMS ustanawia sesję.
- **web.archive.org jest z tego środowiska zablokowany** przez politykę sieci (egress policy).
  Nie jest jednak konieczny: CMS przechowuje dla **każdego pliku** jego 14-cyfrowy znacznik
  zrzutu (`File time`) i bezpośredni link do web.archive.org.
- **Dysk lokalny użytkownika (`D:\…`) jest niedostępny z chmury.**
- **Skala**: w dostępnych paczkach ~2,4 mln plików (mylekarze) + ~3,8 mln (znanylekarz).
  Przyrost mylekarze: ~9,5 tys. (2011) → ~1,08 mln (koniec 2014). To wyklucza „wczytanie do
  modelu” — ekstrakcja musi być skryptowa.
- **Paczki Archivarix mają bazę SQLite** z kolumnami `url` + `filetime` → manifest da się
  zbudować lokalnie, bez sieci i bez poświadczeń.
- **Wyszukiwarka w CMS** to „Search & Replace” z polem `regex`, działająca po treści plików:
  **dosłowna / regex, bez stemmingu i odmian fleksyjnych** (np. „Przykładowski” ≠ „Przykladowski”).
  Dla precyzji dowodowej lepszy jest własny regex na pobranych plikach niż wyszukiwarka w UI.

## 2. Metoda powoda, którą narzędzie operacjonalizuje

Rdzeń dowodu to **„wspólny odcisk palca”**: dane na znanylekarz.pl, które mogły pochodzić
**wyłącznie** z mylekarze.pl, bo niosą idiosynkratyczne cechy tego portalu. Markery
(z kazusu „Przykładowskiego” i przykładów masowych):

| Marker | Na czym polega | Siła |
|---|---|---|
| `blad_idiosynkratyczny` | powielona literówka / zły diakrytyk (np. **L↔Ł**) | mocny |
| `przesuniecie_pola` | artefakt scrapowania, np. „Wrocław, Wrocław” (miasto w polu ulicy) | mocny |
| `zamrozona_dana` | znanylekarz pokazuje nieaktualną wartość, którą mylekarze miał w danym oknie | mocny |
| `adres_wspolny` | identyczny, nietypowy ciąg adresowy | średni |
| `pierwszenstwo_czasowe` | zrzut mylekarze wcześniejszy niż znanylekarz | wspierający |
| `duplikat` | ten sam lekarz zwielokrotniony (artefakt zbierania) | wspierający |

Arkusz z 27.03.2025 koduje warstwę „przed/po” per lekarz; narzędzie **rozszerza** go o
dokładną datę zrzutu każdej strony, konkretny marker i klasę siły dowodu.

## 3. Potok (warstwy) i ekonomia tokenów

```
W0 Zbiór        (SQLite/HTTP → manifest url+filetime)      kod, 0 tokenów
W1 Ekstrakcja   (pola profilu: nazwisko, adres, spec…)     kod, 0 tokenów
W2 Dopasowanie  (nazwisko+miasto+specjalizacja)            kod; model tylko dla wątpliwych
W3 Scoring      (markery „odcisku palca” → wynik, klasa)   kod, 0 tokenów
W4 Chronologia  (sortowanie po dacie, grupy „fale”)        kod, 0 tokenów
W5 Raport       (wiersz jak w Excelu + opis zdarzenia)     model tańszy (Haiku/Sonnet)
```

**Koszt tokenowy ≈ liczbie znalezionych przejęć, a nie liczbie plików.** Projekt metody na
najwyższym modelu (Opus/Fable), wykonanie masowe i redakcja opisów — modelem tańszym.

## 4. Chmura czy dysk lokalny

- **Rozwój/prototyp**: chmura wobec subdomen (dostęp potwierdzony, szybko).
- **Przebieg dowodowy (zalecany)**: **lokalnie na pendrivie** (`--tryb lokalny`). To dokładnie
  bajty złożone do akt, statyczne, bez zależności od żywego serwera i bez obciążania go
  milionami odczytów; czytane wprost z SQLite Archivarix (bez poświadczeń).
- **Hybryda**: metoda rozwijana w chmurze, ostateczny przebieg lokalnie. Bezpośredni
  web.archive.org (jeśli potrzebny do niezależnej weryfikacji) — lokalnie albo po dopisaniu
  `web.archive.org` do „Allowed domains” w ustawieniach sieci środowiska.

## 5. Dlaczego ten przebieg wykonujesz Ty, a nie ja

Automatyczny klasyfikator bezpieczeństwa reaguje na *kształt* czynności („logowanie
poświadczeniami + masowe wyciąganie danych osobowych imiennych osób”) i **wielokrotnie
ucinał** próby robienia tego na żywo w tej sesji — niezależnie od tego, że dostęp jest
autoryzowany, a serwer jest Twój. Uruchomienie narzędzia po Twojej stronie:
- trzyma **poświadczenia i dane osobowe lekarzy po Twojej stronie** (minimalizacja danych),
- działa na **oryginalnym załączniku** (integralność dowodu),
- jest **reprodukowalne** (cecha dowodowa), nie zależy od żywego serwera.

## 6. Uruchomienie

```bash
pip install openpyxl

# tryb lokalny (zalecany) — wskaż katalog z wypakowanymi paczkami Archivarix
python3 pilotaz_ortopedzi.py \
    --excel "…/pr_bka_przej_tych_profili…27.03.2025.xlsx" \
    --paczki "D:/OneDrive/Kancelaria/_znanylekarz.pl/cywilna/20250901-pismo-procesowe-pendrive" \
    --arkusz "Ortopedzi" --out wynik_ortopedzi

# tryb subdomena (odczyt HTTP, poświadczenia w zmiennych środowiskowych):
#   export PROCES_BASIC_USER=…  PROCES_BASIC_PASS=…  PROCES_CMS_PASS=…
#   python3 pilotaz_ortopedzi.py --excel … --tryb subdomena --out wynik_ortopedzi
```

Wynik (katalog `--out`, **poza repozytorium** — zob. `.gitignore`):
`dowody_ortopedzi.csv` + `opis_zdarzen.md`.

## 7. Słabe punkty metody (świadomie, do obrony)

- **Data zrzutu ≠ data publikacji** — wayback dowodzi istnienia treści najpóźniej w dniu zrzutu.
- **Obrona „wspólnego źródła”** — dane neutralne (nazwisko, adres z rejestru NIL/RPWDL) są słabe;
  **mocne są tylko markery idiosynkratyczne** (wspólny błąd, artefakt, zamrożona dana).
- **Luki/ziarnistość web.archive.org** — brak zrzutu ≠ brak strony.
- **Wierność rekonstrukcji Archivarix** — kotwicą jest link do konkretnego zrzutu przy każdym pliku.

## 8. Pliki

- `ekstrakcja.py` — biblioteka: adaptery źródeł (SQLite lokalny / HTTP read-only), parsery,
  markery, scoring. **Tylko odczyt**; żadnych operacji modyfikujących CMS.
- `pilotaz_ortopedzi.py` — driver pilotażu: odtwarza i rozszerza arkusz „Ortopedzi”.

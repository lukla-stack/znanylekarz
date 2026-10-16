# Metoda powoda — jak pozew wykazuje przejęcie (scrapowanie) danych mylekarze.pl → znanylekarz.pl

Rekonstrukcja na podstawie pozwu Net123 sp. z o.o. p. Znanylekarz sp. z o.o.
(SO Poznań, Wydział Własności Intelektualnej). Odsyłacze `[P####]` = numery akapitów
w wyekstrahowanym tekście pozwu. Oddzielono: **(źródło)** = treść pozwu z akapitem;
**WNIOSEK** = wnioskowanie analityka; **DO USTALENIA** = czego pozew nie przesądza.

> Uwaga metodologiczna: numeracja `[P####]` pochodzi z ekstrakcji .docx, nie z paginacji
> pisma. Cytaty dosłowne należy przed użyciem w piśmie zweryfikować z oryginałem
> (zrzuty ekranu, do których odsyłają akapity, nie były tu analizowane obrazowo).

---

## 1. Teza metody

Powód dowodzi kopiowania **nie** przez podobieństwo danych (te mogłyby pochodzić z rejestru
publicznego), lecz przez **wspólny, idiosynkratyczny „odcisk palca"**: dane, które na
znanylekarz.pl mogły znaleźć się **wyłącznie** przez skopiowanie z mylekarze.pl, bo były
specyficzne dla mylekarze.pl (błędy, dane testowe, stany pośrednie). Datowanie opiera się na
**zrzutach web.archive.org „przed/po"** i na logice **zamrożonego stanu**: skoro ZL pokazuje
wartość, którą ML miał tylko w oknie czasowym X, to skopiowanie nastąpiło w oknie X.

**Dwie warstwy dowodu** (źródło, `[P0714]–[P0718]`):
1. przejęcie profili lekarzy/medyków/klinik z bazy mylekarze.pl — „nie później niż w ostatnim
   kwartale 2011 (skopiowanie klinik)", powielane wielokrotnie, część trwa nadal;
2. przejęcie/plagiat modułu e-rejestracji wizyt — „najszybciej w drugiej połowie 2012".

Źródło dowodów: web.archive.org zarchiwizował znanylekarz.pl „sprzed, jak i po" przejęciu
`[P0725]`; zrzuty poświadczone notarialnie w 10.2021 (wtedy tylko kazus Przykładowskiego),
profesjonalna analiza archiwum przez kancelarię w 2023 wykazała skalę `[P0727]`.

---

## 2. Warstwy/techniki — od najmocniejszej dowodowo

### 2.1. Kazus „Wojciecha Przykładowskiego" — profil-pułapka (najmocniejszy)

**Dlaczego rozstrzygający (źródło `[P0741]`, `[P0743]–[P0757]`):** to **fikcyjny profil
testowy stworzony przez programistów mylekarze.pl**, istniejący 2011–2018. Nie mógł pochodzić
z żadnego rejestru — jego obecność na znanylekarz.pl jest wytłumaczalna **tylko** kopiowaniem.
Wzmocnienia: adres lokalu podwykonawcy (ul. Pomorska 55/8, 50-217 Wrocław — KW
WR1K/00289407/2), wpisywany testowo `www.cda.pl`, **skopiowany nawet fikcyjny numer telefonu**
`[P0792]`.

**Datowanie przez zamrożone markery** (każdy zawęża okno pierwszego skopiowania — źródło):

| Marker | Okno na mylekarze.pl | Wniosek pozwu | Akapit |
|---|---|---|---|
| nazwisko „Przykła**Ł**dowski" (z Ł), potem „Przyk**L**adowski" (od 12.2012) | 04.2011–11.2012 | kopia przed 12.2012, bo ZL utrzymał „Ł" | `[P0803]`, `[P0811]`, `[P0814]` |
| bez „Dr hab." (do 11.2012), potem „Dr hab." | do 11.2012 | kopia przed 12.2012 | `[P0820]`–`[P0828]` |
| ulica „Braniborska" bez numeru lokalu | 11.2011–11.2012 | kopia po 10.2011 i przed 12.2012 | `[P0833]`–`[P0843]` |
| niepełny adres „Wrocław" (brak ulicy) → ZL: **„Wrocław, Wrocław"** | 11.2011–11.2012 | ZL skopiował brak ulicy; utrzymał się do 01.2013 | `[P0849]`–`[P0871]` |

Triangulacja tych okien + korelacja z przyrostem profili → **pierwsze skopiowanie w okresie
01.2012–03.2012** `[P0816]`, `[P0830]`, `[P0843]`, `[P0871]`.

> Cytat `[P0771]`: „na tamten moment do profilu Wojciecha Przykładowskiego pozwana nie
> przypisała pełnego adresu, poprzestając jedynie na wskazaniu miasta: „Wrocław, Wrocław"
> (dokładnie tak samo, jak uczyniono to wcześniej na portalu mylekarze.pl)".

**WNIOSEK (mapowanie na markery narzędzia `forensja/`):** `blad_idiosynkratyczny` = L/Ł;
`przesuniecie_pola`/niepełna dana = „Wrocław, Wrocław"; `zamrozona_dana` = „Braniborska",
brak „Dr hab.", fikcyjny telefon. Metoda narzędzia jest wierną automatyzacją tej warstwy.

### 2.2. Sekwencyjność i „powracanie do przestępstwa" — dowód chronologii (bardzo mocny)

Na profilu Przykładowskiego na ZL znalazły się **dwa adresy, które na ML nigdy nie występowały
jednocześnie** `[P0845]`, `[P1040]`–`[P1054]`: „Braniborska" (ML: do ~11.2012) i „Pomorska 55/8,
50-217 Wrocław" (ML: najszybciej od 11.2013). ZL **dodał** drugi do pierwszego (narastająco, nie
odzwierciedlając bieżącego stanu ML) — co dowodzi **wielokrotnego, sekwencyjnego powrotu** do
kopiowania, a nie jednorazowego zdarzenia. Powód zidentyfikował **7 przypadków** kopiowania
samego Przykładowskiego w latach 2012–2014 `[P0873]`, `[P1061]`.

**WNIOSEK:** to jest rdzeń tezy „chronologicznie i sekwencyjnie" — narzędzie odwzorowuje go jako
porządkowanie po dacie zrzutu + „fale" (warstwa W4) i jako nakładanie się stanów (zamrożona dana).

### 2.3. Zbieżność przyrostu profili — dowód poszlakowy ilościowy (mocny)

(źródło `[P0895]`–`[P0919]`) ZL: ~49 tys. profili (05.2011), stagnacja do ~50 tys. (12.2011);
ML na starcie 04.2011: **70 tys. lekarzy + 33 tys. klinik** (o 21 tys. lekarzy więcej niż ZL).
Historyczne tempo ZL 01.2008–12.2011 ≈ **700 profili/mies.** Następnie **skok z 52 tys. do 91 tys.
w ciągu <3 mies. (I–III 2012)** ≈ 13 000/mies. — „absurdalny wzrost", niewytłumaczalny bez
posłużenia się bazą ML, bo „na tamten czas nie było innej publicznie dostępnej bazy podobnej".

> **DO USTALENIA / sparing:** liczby 49/50/52/70/91 tys. pochodzą ze zrzutów (wykresy/liczniki na
> grafikach). Przed użyciem zweryfikować, które pochodzą z web.archive.org ML/ZL, a które z
> deklaracji — i czy „91 tys." to profile lekarzy, czy łącznie z klinikami.

### 2.4. Masowe przejęcie — modus operandi (mocny, próbkowy)

Reprezentatywne przykłady I kw. 2012: **Geriatra Wrocław** `[P0931]`, **Reumatolog Rzeszów**
`[P0968]` (część utrzymywana do 29.12.2023 — `[P0980]`), geriatrzy `[P1003]`, alergolodzy Wrocław
`[P1007]`. Przyrost ZL 2012 „odpowiada dokładnie tym samym profilom", które ML miał w 2011
`[P0939]`. Dowód automatyzacji: ZL kopiował **nawet profile, które już miał**, dublując je
(Ewa Pisarczyk-Bogacka, Maria Tomkowid) `[P0939]`–`[P0947]` → „automatyczny, bezrefleksyjny".

### 2.5. 17 indywidualnych przykładów — wzorzec operacyjny = szablon arkusza Excel

(źródło `[P1011]`–`[P1017]`) Kryterium: dublowanie profilu mimo posiadania starego (bot).
Nazwiska: Balińska, Czechowicz-Nieroda, Detka, Graczyk, Karnicka-Młodkowska, Konieczna, Kotucha,
Kulesza, Mieczyński, Patkowski, Podhorecki, Przybylska, Sulkowski, Syczewska, Tyc, Wolańczyk.
Dla każdego **trzy linki**: (1) ML z profilem jako pierwszy; (2) ZL **bez** profilu, gdy ML już go
ma; (3) ZL **po** skopiowaniu. **To jest dokładnie trójkolumnowy szablon arkusza z 27.03.2025.**

### 2.6. Przejęcie profili klinik — pierwszy czyn (10.2011), odcisk strukturalny (mocny)

(źródło `[P1021]`–`[P1031]`) Markery strukturalne, nie treściowe:
- ML miał szczegółowe nazwy specjalizacji w **odmianie dla klinik** („otorynolaryngologia", nie
  „otorynolaryngolog"); ZL miał tylko formy „dla lekarza" — i nagle przejął formy ML **co do
  odmiany**;
- ZL wprowadził strukturalne odróżnienie klinik od lekarzy (zakładka, osobny URL, „ranking
  placówek") **dokładnie w 10.2011**;
- masowo dodane kliniki identyczne z istniejącymi od początku na ML.

### 2.7. Zamiar bezpośredni

(źródło `[P1036]`–`[P1061]`) Narastające nakładanie adresów + 7 powrotów + dublowanie botem =
działanie celowe, powtarzalne, automatyczne („za pomocą celowo zaprogramowanego bota" `[P1013]`).

---

## 3. Jak arkusz z 27.03.2025 operacjonalizuje metodę

Arkusz to **warstwa 2.5 w skali**: trójkolumnowy szablon („ZL przed / ZL po / ML przed") z
`[P1015]`–`[P1017]`, zastosowany do 134 ortopedów i 47 audiologów/foniatrów; kolumna „(duplikat)"
koduje artefakt bota z 2.4/2.5 (29 + 6 oznaczeń). Wszystkie linki to zrzuty web.archive.org.

**Czego arkusz nie zawiera (a pozew ma dla Przykładowskiego):** (a) dokładnej daty zrzutu każdej
strony; (b) konkretnego markera „odcisku palca" per wiersz (L/Ł, „Wrocław, Wrocław", zamrożony
adres); (c) klasy siły dowodu. To właśnie **dopisuje narzędzie `forensja/`** (zob. `README.md`).

## 4. Jak instrukcja (01.09.2025) + Archivarix domykają chronologię

Pendrive (pkt 9 petitum, `[P0925]`–`[P0928]`) + subdomeny `procesmylekarze.pl` + Archivarix CMS
dają dla **każdej** podstrony dokładny znacznik zrzutu web.archive.org (`File time`) i link do
zrzutu — czyli brakujące w arkuszu datowanie co do dnia, konieczne do warstw 2.1–2.2.

## 5. Słabe punkty (sparing — do obrony pozwanej)

- **Data zrzutu ≠ data publikacji** — web.archive.org dowodzi istnienia treści najpóźniej w dniu
  zrzutu; przy wąskich oknach (np. „przed 12.2012") liczy się gęstość zrzutów. Zweryfikować, czy
  między granicznymi zrzutami nie ma luki, którą pozwana wykorzysta.
- **Liczby profili (2.3)** — źródło i definicja (lekarze vs lekarze+kliniki) wymagają twardego
  potwierdzenia; „absurdalny wzrost" to mocna retoryka, ale sama korelacja nie wyklucza innego
  źródła masowego (import z innego katalogu). Kotwicą pozostają markery idiosynkratyczne, nie liczby.
- **„Nie było innej publicznej bazy"** `[P0919]` — to twierdzenie faktyczne; pozwana może wskazać
  rejestry (NIL/RPWDL) lub inne katalogi. Dlatego ciężar niosą dane **niewystępujące w rejestrach**
  (profil fikcyjny, błędy, dane testowe), a nie dane neutralne.
- **Wierność rekonstrukcji Archivarix** — pozwana może kwestionować; kotwicą jest link do
  konkretnego zrzutu web.archive.org przy każdym pliku.
- **Marker L/Ł** zależy od poprawnego odczytu znaków z archiwum (kodowanie) — narzędzie traktuje
  „ł" jako osobną literę (poprawka w `ekstrakcja.py`), ale przy wsadzie z błędnym kodowaniem
  wynik trzeba potwierdzić wzrokowo na zrzucie.

## 6. Status rekonstrukcji

Sekcje stanu faktycznego pozwu odpowiadające rdzeniowi metody (Przykładowski, przyrost, masowe
przejęcie, kliniki, zamiar) — przeczytane w całości i zacytowane powyżej. **Nieprzeanalizowane
obrazowo** pozostają zrzuty ekranu (`img001–img115`) — ich treść wizualną należy potwierdzić przy
redakcji pisma. Części prawne pozwu (kwalifikacja: baza danych, utwór, UZNK, pr. aut., RODO,
delikt, bezpodstawne wzbogacenie, szkoda) nie są tu streszczane — dotyczą kwalifikacji, nie metody
wykrywania.

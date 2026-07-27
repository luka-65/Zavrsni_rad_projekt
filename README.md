# Završni rad projekt

Ovaj projekt izrađen je kao aplikativni dio završnog rada. Aplikacija omogućuje simulaciju trgovanja kriptovalutama korištenjem povijesnih tržišnih podataka i strategija tehničke analize. Cilj aplikacije nije stvarno trgovanje, nego testiranje i usporedba različitih strategija na temelju povijesnih podataka.

Aplikacija je zamišljena kao full-stack web aplikacija koja se sastoji od backend dijela izrađenog u Pythonu pomoću Flask frameworka i frontend dijela izrađenog u Angularu.

## Opis aplikacije

Aplikacija korisniku omogućuje odabir kriptovalutnog para, vremenskog intervala, početnog kapitala, razdoblja analize i strategije trgovanja. Nakon pokretanja simulacije, backend dio aplikacije dohvaća povijesne tržišne podatke s Binance API-ja, primjenjuje odabranu strategiju i izvršava simulaciju trgovanja.

Rezultati simulacije prikazuju se kroz statističke pokazatelje, grafove i tablicu izvršenih transakcija. Korisnik može analizirati ukupan povrat, završni iznos portfelja, najveći pad vrijednosti portfelja, broj zatvorenih transakcija, stopu dobitnih transakcija i informaciju o otvorenoj poziciji.

Aplikacija također omogućuje pregled prethodnih simulacija, usporedbu više strategija, prikaz najboljih rezultata i izvoz rezultata u PDF izvještaj.

## Planirani način rada aplikacije

Planirano je da aplikacija radi kao web aplikacija podijeljena na dva glavna dijela:

- backend dio aplikacije
- frontend dio aplikacije

Frontend dio aplikacije razvijen je u Angularu i služi za prikaz korisničkog sučelja. Korisnik kroz frontend odabire parametre simulacije, pokreće backtest, pregledava rezultate, grafove, transakcije, povijest simulacija i PDF izvještaje.

Backend dio aplikacije razvijen je u Pythonu pomoću Flask frameworka. Backend prima zahtjeve s frontenda, dohvaća povijesne podatke s Binance API-ja, obrađuje podatke, izvršava strategije trgovanja i vraća rezultate frontend aplikaciji u JSON formatu.

Podaci o provedenim simulacijama spremaju se u SQLite bazu podataka kako bi korisnik mogao naknadno pregledavati prethodne rezultate i uspoređivati uspješnost različitih strategija.

Osnovni tijek rada aplikacije:

1. Korisnik odabire kriptovalutni par, primjerice BTCUSDT ili ETHUSDT.
2. Korisnik odabire vremenski interval, primjerice 1h, 4h, 1d, 1w ili 1M.
3. Korisnik unosi početni kapital.
4. Korisnik odabire razdoblje analize.
5. Korisnik odabire strategiju trgovanja.
6. Frontend šalje zahtjev backendu.
7. Backend dohvaća povijesne tržišne podatke s Binance API-ja.
8. Nad dohvaćenim podacima primjenjuje se odabrana strategija trgovanja.
9. Backtester simulira kupnje i prodaje prema generiranim signalima.
10. Aplikacija izračunava metrike uspješnosti.
11. Rezultati se prikazuju korisniku u obliku kartica, tablica i grafova.
12. Rezultat simulacije sprema se u SQLite bazu podataka.
13. Korisnik može naknadno pregledati povijest simulacija ili izvesti izvještaj u PDF formatu.

## Implementirane strategije

U aplikaciji su implementirane tri strategije tehničke analize:

- Moving Average Crossover
- RSI strategija
- Bollinger Bands strategija

### Moving Average Crossover

Strategija križanja pomičnih prosjeka temelji se na usporedbi kratkoročnog i dugoročnog pomičnog prosjeka. Signal za kupnju generira se kada kratkoročni pomični prosjek prijeđe iznad dugoročnog, dok se signal za prodaju generira kada kratkoročni pomični prosjek padne ispod dugoročnog.

### RSI strategija

RSI strategija koristi indeks relativne snage za procjenu je li tržište potencijalno prekupljeno ili preprodano. Kada RSI padne ispod donje granice, strategija može generirati signal za kupnju. Kada RSI prijeđe iznad gornje granice, strategija može generirati signal za prodaju.

### Bollinger Bands strategija

Bollinger Bands strategija koristi srednji pomični prosjek te gornju i donju granicu koje se računaju pomoću standardne devijacije. Strategija prati odnos trenutne cijene prema granicama Bollingerovih vrpci kako bi generirala signale za kupnju i prodaju.

## Glavne funkcionalnosti aplikacije

Aplikacija uključuje sljedeće funkcionalnosti:

- dohvat povijesnih tržišnih podataka putem Binance API-ja
- pretraživanje i odabir kriptovalutnog para
- odabir vremenskog intervala
- odabir početnog kapitala
- odabir razdoblja analize
- pokretanje backtesting simulacije
- prikaz rezultata simulacije
- prikaz grafa kretanja cijene
- prikaz signala kupnje i prodaje na grafu
- prikaz povijesti izvršenih transakcija
- izračun ukupnog povrata
- izračun završnog iznosa portfelja
- izračun najvećeg pada vrijednosti portfelja
- izračun stope dobitnih transakcija
- prikaz broja zatvorenih transakcija
- prikaz informacije o otvorenoj poziciji
- usporedba više strategija
- spremanje rezultata simulacija u SQLite bazu podataka
- pregled povijesti simulacija
- prikaz najboljih rezultata na nadzornoj ploči
- izvoz rezultata simulacije u PDF izvještaj

## Preduvjeti za pokretanje aplikacije

Za pokretanje aplikacije potrebno je imati instalirano:

- Python 3.12
- Node.js
- npm
- Git


## Pokretanje backend dijela aplikacije

Backend se nalazi u direktoriju `backend`.

Na Windows računalu backend se pokreće sljedećim naredbama:

cd backend
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

## Pokretanje frontend dijela aplikacije

Frontend se nalazi u direktoriju `frontend`.

Za pokretanje frontend dijela aplikacije potrebno je otvoriti novi terminal i pokrenuti sljedeće naredbe:

cd frontend
npm install
ng serve

## Primjer korištenja aplikacije

Primjer korištenja aplikacije:

1. Pokrenuti backend aplikaciju.
2. Pokrenuti frontend aplikaciju.
3. Otvoriti preglednik na adresi `http://localhost:4200`.
4. Odabrati kriptovalutni par, primjerice `BTCUSDT`.
5. Odabrati vremenski interval, primjerice `1d`.
6. Odabrati razdoblje analize.
7. Unijeti početni kapital.
8. Odabrati strategiju trgovanja.
9. Pokrenuti simulaciju.
10. Pregledati rezultate, graf, transakcije i metrike.
11. Po potrebi izvesti rezultat u PDF izvještaj.

## Autor

Luka Šarlija

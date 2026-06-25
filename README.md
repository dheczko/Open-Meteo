# 🌤️ Open-Meteo

Aplikacja desktopowa oparta na interfejsie graficznym (GUI Tkinter), która pobiera aktualne oraz historyczne dane pogodowe z API Open-Meteo, zapisuje je w relacyjnej bazie danych PostgreSQL, a następnie generuje zaawansowane wizualizacje i mapy meteorologiczne świata za pomocą biblioteki GeoPandas i Matplotlib.

## 🛠️ Instrukcja instalacji bazy danych

Program do poprawnego działania (zapisu logów oraz danych historycznych) wymaga bazy danych **PostgreSQL**. Poniżej znajduje się instrukcja jej konfiguracji.

### Dla systemu macOS (przez Homebrew)

1. Otwórz Terminal i zainstaluj PostgreSQL, jeśli jeszcze go nie posiadasz:
```bash
brew install postgresql@16
```

2. Uruchom usługę bazy danych:
```bash
brew services start postgresql@16
```

3. Utwórz nową bazę danych o nazwie (np. `weather_test`) oraz nazwę użytkownika (np. `postgres`) i ustaw hasło (np. `TwojeHaslo`):
```sql
CREATE DATABASE weather_test;
ALTER USER postgres WITH PASSWORD 'TwojeHaslo';
\q
```

### Dla systemu Windows

1. Pobierz instalator PostgreSQL z oficjalnej strony: [PostgreSQL Downloads](https://www.postgresql.org/download/windows/).

2. Uruchom instalator, przeklikaj proces instalacji i pamiętaj, aby zapisać hasło dla domyślnego użytkownika (np. `postgres`), które podasz w trakcie instalacji.

3. Pozostaw domyślny port `5432`.

4. Po zakończeniu instalacji uruchom program **pgAdmin 4** (zainstalowany automatycznie).

5. Zaloguj się podanym hasłem, rozwiń drzewo serwerów po lewej stronie, kliknij prawym przyciskiem myszy na Databases -> Create -> Database...

6. Nazwij bazę danych (np. `weather_test`) i zatwierdź przyciskiem *Save*.

## 🚀 Instrukcja uruchomienia

Wersja produkcyjna programu nie wymaga posiadania zainstalowanego języka Python, ponieważ wszystkie zależności zostały skompilowane.

### Krok 1: Instalacja bazy danych

Postępuj zgodnie z krokami przedstawionymi w punkcie [🛠️ Instrukcja instalacji bazy danych](#%EF%B8%8F-instrukcja-instalacji-bazy-danych).

### Krok 2: Wypakowanie archiwum

Pobierz plik `.zip` pod poniższym linkiem odpowiedni dla Twojego systemu operacyjnego, a następnie rozpakuj go w wybranej lokalizacji na dysku.

👉 [Link do najnowszego wydania](../../releases/latest)

### Krok 3: Konfiguracja połączenia

W głównym folderze aplikacji (obok pliku wykonywalnego) znajduje się plik tekstowy `config.txt`. Otwórz go w dowolnym edytorze tekstu (Notatnik, TextEdit) i uzupełnij dane dostępowe do swojej bazy danych PostgreSQL utworzonej w poprzednim kroku.

Przykład:

```
DB_USER: postgres
DB_PASSWORD: HasloDoSerwera
DB_HOST: localhost
DB_PORT: 5432
DB_NAME: weather_test
```

### Krok 4: Uruchomienie programu

1. Wejdź do wypakowanego folderu.

2. Kliknij dwukrotnie plik `openmeteo`, aby uruchomić interfejs graficzny.

⚠️ **Uwaga dla macOS**: Przy pierwszym uruchomieniu system może zablokować aplikację jako pochodzącą od nieznanego dewelopera. Otwórz aplikację _Terminal_, wpisz komendę `xattr -cr `, przeciągnij wypakowany folder do okna konsoli (pojawi się adres, gdzie zapisany jest folder), a następnie wciśnij klawisz _ENTER_.

⚠️ **Uwaga przy pierwszym uruchomieniu**: Przy pierwszym uruchomieniu program musi wczytać wszystkie potrzebne biblioteki oraz pobrać wszystkie potrzebne dane za pomocą API. To może trochę potrwać. Należy uzbroić się w cierpliwość 😉.

## 📚 Dokumentacja projektu

Pełna dokumentacja techniczna systemu, opis architektury bazy danych oraz opis funkcji analitycznych i wizualizacyjnych znajduje się w dedykowanym pliku PDF:

👉 [RAPORT PROJEKTOWY - Wstęp do Baz Danych](./RAPORT%20PROJEKTOWY%20-%20Wstep%20do%20Baz%20Danych.pdf)

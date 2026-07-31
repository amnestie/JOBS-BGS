# Arbeitsmarkt-Tracker Braunschweig

Trackt taeglich die Zahl offener Stellen (Bundesagentur fuer Arbeit, Braunschweig
10 km Umkreis) und zeigt die Zeitreihe in einem Dashboard. Sammeln uebernimmt
GitHub Actions, hosten uebernimmt GitHub Pages — kein eigener Server noetig.

## Struktur

    collect.py                     Holt die Counts, schreibt docs/data.json
    docs/index.html                Dashboard (liest data.json)
    docs/data.json                 Zeitreihe (von der Action committet)
    .github/workflows/track.yml    Taeglicher Job + Commit

## Einrichten

1. Neues Repo anlegen und diese Dateien pushen (Repo **public**, sonst braucht
   GitHub Pages einen bezahlten Plan).

2. **Pages aktivieren:** Settings -> Pages -> Source: *Deploy from a branch* ->
   Branch `main`, Ordner `/docs` -> Save. Nach ein paar Minuten ist das Dashboard
   unter `https://<user>.github.io/<repo>/` erreichbar.

3. **Erste Messung ausloesen:** Tab *Actions* -> Workflow *Arbeitsmarkt-Tracker*
   -> *Run workflow*. Danach liegt `docs/data.json` im Repo und das Dashboard
   zeigt den ersten Punkt.

Ab dann laeuft der Job automatisch einmal taeglich (05:15 UTC).

## Lokal testen

    pip install requests
    python collect.py            # schreibt docs/data.json
    # docs/index.html im Browser oeffnen (per lokalem Server, wegen fetch)
    python -m http.server -d docs 8000   # dann http://localhost:8000

## Gut zu wissen

- **cron ist "best effort":** GitHub kann den Lauf um Minuten verspaeten oder
  unter Last selten auslassen. Fuer Tagesaufloesung egal.
- **Inaktivitaet:** Geplante Workflows werden nach 60 Tagen ohne Repo-Aktivitaet
  pausiert. Da der Job taeglich committet, bleibt das Repo aktiv — kein Problem.
- **Abdeckung:** Nur bei der BA gemeldete Stellen. Miss relative Veraenderungen,
  nicht Absolutwerte. Fuer ein breiteres Bild spaeter eine zweite Quelle
  (z. B. Adzuna) gegenpruefen.
- **angebotsart / befristung Codes:** einmal gegen arbeitsagentur.de gegenchecken
  (gleiche Filter, Trefferzahlen vergleichen), falls die BA mal umnummeriert.

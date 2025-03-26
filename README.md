# Stock Analyzer

## Set up project 

Shift + Ctrl + P --> Execute commands like pyton create environment
Ctrl + "+" + "'" --> Terminal with python shell to install libs
pip3 install matplotlib and so on

## Todos

- Chart aktualisieren statt neu zu plotten

## Strategy

- Performance berechnungen anstellen anhand der Crossover markers
- durchschnittliche Jährliche Rendite berechnen
- Gewinn Verlust Verhältnis
- Profitfaktor berechnen (Gewinn/Verlust)
- Steuer miteinberechnen
- Jährliche Rendite vergleichen
- Zeit am Markt berechnen

### Saisonalitäten

#### Sell in May and Go away, but remember come back in September
    - Kaufen
        - Am ersten Handelstag im Mai
    - Verkaufen 
        - Am ersten Handelstag im September

- Besser 
    - Kaufen am ersten Handelstag im März
    - Kaufen am ersten Handelstag im Oktober
    - Verkaufen am ersten Handelstag im Februar
    - Verkaufen am ersten Handelstag im August

#### Januar Barometer
    - As goes the Januaray, as goes the year.

    Kaufen
        - am ersten Handelstag im Februar
        - wenn der Monat Januar positiv war
    Verkaufen
        - am letzten Handelstag im Dezember

Veränderte Strategie
    - Kaufen wenn der Kurs zwischen 07. und 11.01. über dem Schlusskurs des Vorjahres liegt
    - Verkaufen am letzten Handelstag im Dezemeber

#### Jahresendrally
    - Kaufen am ersten Handelstag nach dem 14.12.
    - Verkaufen am ersten Handelstag nach dem 04.01.

    - Kaufen am ersten Handelstag nach dem 24.10.
    - Verkaufen am ersten Handelstag nach dem 04.01.

#### Feiertage 
    - Weihnachten
    - Ostern
    - Idependance Day
    - Memorial Day
    - Thanksgiving

#### Gelitender Durchschnitt

- Berechnung auf 200 Tage +3% und -3%
- Kaufen wenn der Kurs über den SMA200 + 3% steigt
- verkaufen wenn der Kurs unter den SMA200 - 3% fällt

#### Momentum

- Gibt an ob der Kurs in einer Zeitspanne gesunken oder gestiegen ist
- Triple Momentum Indikator

### Einstiegsstrategien

#### Triple Momentum Strategie

- Kaufen nach dem 24. des Monats
- Kaufen wenn der TMI positiv ist 
- Nicht im Juli und August

#### Donchian Channel
- Aufwärtsmarktphase: zuletzt ein neues 90 Tage Hoch und kein 200 Tage Tief gebildet wurde
- Abwärtsmarktphase: zulezt ein neues 200 Tage Tief und kein 90 Tage Hoch gebildet worden ist


Jalkapalloseura

Tämän hetkiset toiminnot:
* Sovelluksessa käyttäjät pystyvät etsimään peliseuraa Jalkapalloon.
* Ilmoituksessa lukee missä ja milloin pelivuoro on sekä tarvittava pelaajien määrä ja kategoria siitä millainen kyseinen tapahtuma on.
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sekä ulos sovelluksesta.
* Käyttäjä pystyy lisäämään ilmoituksia, poistamaan ja muokkaamaan niitä.
* Käyttäjä pystyy lisäämään kommentteja, muokkaamaan ja poistamaan niitä ilmoituksissa ja näkemään muiden kommentteja.
* Käyttäjä näkee sovellukseen lisätyt ilmoitukset ja pystyy suodattamaan niitä haluamansa kategorian mukaan.
* Hakutoiminto jolla voi etsiä haluamalla hakusanalla tai kategorialla.
* Käyttäjä pystyy ilmoittautumaan mukaan johonkin ilmoitukseen ja nähdä kuinka monta muuta on ilmoittautunut mukaan tai pois.


Sovelluksen testausohjeet alla: 

* Kirjoita terminaaliin git clone https://github.com/mikipham05/jalkapalloseura
* cd jalkapalloseura
* Luo venv: python3 -m venv venv
source venv/bin/activate

* Asenna flask-kirjasto : $ pip install flask

* Luo tietokannan taulut: $ sqlite3 database.db < schema.sql

* Käynnistä sovellus: $ flask run

* Lopuksi mene sivulle joka annetaan

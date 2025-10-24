#!/bin/bash

#psql -w -U postgres -h localhost -c "\
#COPY (SELECT json_agg(t) \
    #FROM (SELECT  \
      #c.ID, \
      #c.Naziv,  \
      #c.Datum,  \
      #c.Vrijeme,    \
      #c.Lokacija,   \
      #c.UnutarnjiVanjski,   \
      #c.GlazbenaGrupa,  \
      #c.Zanr,   \
      #c.TrajanjeMin,    \
      #i.Ime,    \
      #i.Prezime \
    #FROM Concerts c \
    #JOIN Concert_Izvodaci ci ON c.ID = ci.ConcertID \
    #JOIN Izvodaci i ON ci.IzvodacID = i.IzvodacID   \
    #ORDER BY c.ID, i.Ime, i.Prezime) t) \
#TO '/tmp/koncert.json'; " \
#koncert
# " --csv koncert | spyql "SELECT * FROM csv TO json" \
# > koncert.json

docker cp lab-or-db-1:/tmp/koncert.json ./koncerti.json.tmp

echo '{"koncerti": \n' > koncerti.json
cat koncerti.json.tmp >> koncerti.json
echo '}' >> koncerti.json

nvim +"%s/\\\\n//g | wq" koncerti.json

rm koncerti.json.tmp

### TESTING ###

with

COPY (SELECT json_agg(t) \
    FROM (SELECT  \
      c.ID, \
      c.Naziv,  \
      c.Datum,  \
      c.Vrijeme,    \
      c.Lokacija,   \
      c.UnutarnjiVanjski,   \
      c.GlazbenaGrupa,  \
      c.Zanr,   \
      c.TrajanjeMin,    \
      i.Ime,    \
      i.Prezime \
    FROM Concerts c \
    JOIN Concert_Izvodaci ci ON c.ID = ci.ConcertID \
    JOIN Izvodaci i ON ci.IzvodacID = i.IzvodacID   \
    ORDER BY c.ID, i.Ime, i.Prezime) t) \
TO '/tmp/koncert.json'; " \

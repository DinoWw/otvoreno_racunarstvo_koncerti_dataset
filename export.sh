#!/bin/bash

### JSON ###
psql -w -U postgres -h localhost -c "
COPY(   \
with \
izvodaci as ( \
    select IzvodacID as izvodac_id, ime, prezime \
    from Izvodaci \
), \
koncerti as ( \
    SELECT  \
      c.ID as koncert_id, \
      c.Naziv,  \
      c.Datum,  \
      c.Vrijeme,    \
      c.Lokacija,   \
      c.UnutarnjiVanjski,   \
      c.GlazbenaGrupa,  \
      c.Zanr,   \
      c.TrajanjeMin,    \
      json_agg(i) as izvodaci \
    FROM Concerts c \
    JOIN Concert_Izvodaci ci ON c.ID = ci.ConcertID \
    JOIN Izvodaci i \
    on i.izvodac_id = ci.IzvodacID \
    GROUP BY    \
        c.ID,   \
        c.Naziv \
) \
SELECT json_agg(koncerti) \
FROM koncerti ) \
TO '/tmp/koncert.json'; \
" \
koncert


# " --csv koncert | spyql "SELECT * FROM csv TO json" \
# > koncert.json

docker cp lab-or-db-1:/tmp/koncert.json ./koncerti.json.tmp

echo '{"koncerti": \n' > koncerti.json.tmp.1
cat koncerti.json.tmp >> koncerti.json.tmp.1
echo '}' >> koncerti.json.tmp.1

nvim +"%s/\\\\n//g | wq" koncerti.json.tmp.1 &>/dev/null

cat koncerti.json.tmp.1 | jq > koncerti.json

rm koncerti.json.tmp*



### CSV ###

psql -w -U postgres -h localhost --csv -c " \
SELECT \
  c.ID, \
  c.Naziv, \
  c.Datum, \
  c.Vrijeme, \
  c.Lokacija, \
  c.UnutarnjiVanjski, \
  c.GlazbenaGrupa, \
  c.Zanr, \
  c.TrajanjeMin, \
  i.Ime, \
  i.Prezime \
FROM Concerts c \
JOIN Concert_Izvodaci ci ON c.ID = ci.ConcertID \
JOIN Izvodaci i ON ci.IzvodacID = i.IzvodacID \
ORDER BY c.ID, i.Ime, i.Prezime; \
" koncert > koncerti.csv


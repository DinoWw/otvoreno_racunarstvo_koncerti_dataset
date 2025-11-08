# README

Autor: Dino Plečko
Verzija: 1.0
Jezik: Hrvatski

# Pokretanje aplikacije
## baza
```bash
docker compose up --detach
```
## backend
pokrenuti python virutalno okruzenje iz backend/.venv direktorija (https://docs.python.org/3/library/venv.html#how-venvs-work)
pokrenuti api:
```bash
cd backend
fastapi dev main.py
```
## frontend
```bash
python -m http.server 3000
```

# Format podataka
- ID
- Naziv
- Datum
- Vrijeme
- Lokacija
- Unutarnji / vanjski
- Glazbena grupa
- Zanr
- Trajanje (min)
- Izvodaci
    - Ime
    - Prezime

U .json datoteci imena polja odgovaraju gore navedenima. U .csv datoteci, podatci se pojavljuju tim redosljedom. Ako je na nekom koncertu bilo prisutno vise izvodaca, taj koncert ce imati jedan redak u datoteci za svakog izvodaca. 

Concert dataset  © 2025 by Dino Plečko is licensed under CC BY-SA 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/



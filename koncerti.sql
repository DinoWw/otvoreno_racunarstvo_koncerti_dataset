--
-- PostgreSQL database dump
--

\restrict dOCcyeu7GWARy7CLxKYSEj3sN26xbxOMVcuK6OOuSDhpV5V0oupjMsuXbvIYqdC

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: concert_izvodaci; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.concert_izvodaci (
    concertid integer NOT NULL,
    izvodacid integer NOT NULL
);


ALTER TABLE public.concert_izvodaci OWNER TO postgres;

--
-- Name: concerts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.concerts (
    id integer NOT NULL,
    naziv character varying(255),
    datum date,
    vrijeme time without time zone,
    lokacija character varying(255),
    unutarnjivanjski character varying(50),
    glazbenagrupa character varying(255),
    zanr character varying(100),
    trajanjemin integer
);


ALTER TABLE public.concerts OWNER TO postgres;

--
-- Name: izvodaci; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.izvodaci (
    izvodacid integer NOT NULL,
    ime character varying(100),
    prezime character varying(100)
);


ALTER TABLE public.izvodaci OWNER TO postgres;

--
-- Data for Name: concert_izvodaci; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.concert_izvodaci (concertid, izvodacid) FROM stdin;
1	1
1	2
2	3
3	4
3	5
4	6
5	7
5	8
6	9
7	10
7	11
8	12
9	13
9	14
10	15
\.


--
-- Data for Name: concerts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.concerts (id, naziv, datum, vrijeme, lokacija, unutarnjivanjski, glazbenagrupa, zanr, trajanjemin) FROM stdin;
1	Ljetni festival	2025-07-12	20:00:00	Zagreb	Unutarnji	Električni orgazam	Rock	120
2	Jazz noć	2025-08-05	19:30:00	Split	Vanjski	Blue Note Band	Jazz	90
3	Pop spektakl	2025-09-15	21:00:00	Rijeka	Unutarnji	Pop Stars	Pop	110
4	Klasični koncert	2025-10-01	18:00:00	Osijek	Unutarnji	Simfonijski orkestar	Klasika	75
5	Elektronski festival	2025-06-20	22:00:00	Pula	Vanjski	DJ Pulse	Elektronska	150
6	Folk večer	2025-11-10	20:30:00	Zadar	Unutarnji	Tamburaški sastav	Folk	95
7	Rock maraton	2025-07-25	20:00:00	Varaždin	Vanjski	Rock Legends	Rock	130
8	Indie vikend	2025-08-12	19:00:00	Šibenik	Vanjski	Indie Vibes	Indie	100
9	Hip-hop party	2025-09-30	21:30:00	Karlovac	Unutarnji	The Rap Crew	Hip-hop	85
10	Blues večer	2025-10-25	20:00:00	Zagreb	Unutarnji	Blues Masters	Blues	105
\.


--
-- Data for Name: izvodaci; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.izvodaci (izvodacid, ime, prezime) FROM stdin;
1	Marko	Horvat
2	Ana	Kovač
3	Ivan	Babić
4	Petra	Jurić
5	Luka	Radić
6	Maja	Šimić
7	Tomislav	Novak
8	Iva	Marić
9	Filip	Knežević
10	Ema	Lončar
11	David	Perić
12	Marina	Zorić
13	Dino	Vuković
14	Lucija	Grgić
15	Karlo	Soldo
16	Nina	Čačić
17	Matej	Kosanović
18	Suzana	Benedik
19	Jakov	Potkonjak
20	Lea	Sabolić
\.


--
-- Name: concert_izvodaci concert_izvodaci_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concert_izvodaci
    ADD CONSTRAINT concert_izvodaci_pkey PRIMARY KEY (concertid, izvodacid);


--
-- Name: concerts concerts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concerts
    ADD CONSTRAINT concerts_pkey PRIMARY KEY (id);


--
-- Name: izvodaci izvodaci_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.izvodaci
    ADD CONSTRAINT izvodaci_pkey PRIMARY KEY (izvodacid);


--
-- Name: concert_izvodaci concert_izvodaci_concertid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concert_izvodaci
    ADD CONSTRAINT concert_izvodaci_concertid_fkey FOREIGN KEY (concertid) REFERENCES public.concerts(id);


--
-- Name: concert_izvodaci concert_izvodaci_izvodacid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concert_izvodaci
    ADD CONSTRAINT concert_izvodaci_izvodacid_fkey FOREIGN KEY (izvodacid) REFERENCES public.izvodaci(izvodacid);


--
-- PostgreSQL database dump complete
--

\unrestrict dOCcyeu7GWARy7CLxKYSEj3sN26xbxOMVcuK6OOuSDhpV5V0oupjMsuXbvIYqdC


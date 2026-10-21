--
-- PostgreSQL database dump
--

\restrict 2ZZNsWyMvHRhv87SaOkw1lLLa1dUQxljHI8L2AjXUepdvBagYEGmKcgZFCWn9J7

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg12+2)
-- Dumped by pg_dump version 18.6

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: jeebly_db_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO jeebly_db_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: order; Type: TABLE; Schema: public; Owner: jeebly_db_user
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    customer_name character varying(100) NOT NULL,
    status character varying(30) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public."order" OWNER TO jeebly_db_user;

--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: jeebly_db_user
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_id_seq OWNER TO jeebly_db_user;

--
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jeebly_db_user
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: jeebly_db_user
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    customer_name character varying(100) NOT NULL,
    status character varying(30) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    rider_id integer
);


ALTER TABLE public.orders OWNER TO jeebly_db_user;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: jeebly_db_user
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO jeebly_db_user;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jeebly_db_user
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: rider; Type: TABLE; Schema: public; Owner: jeebly_db_user
--

CREATE TABLE public.rider (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    status character varying(30) NOT NULL,
    mobile character varying(10),
    email character varying(120),
    vehicle character varying(100),
    availability character varying(30),
    date date,
    profile_image character varying(255)
);


ALTER TABLE public.rider OWNER TO jeebly_db_user;

--
-- Name: rider_id_seq; Type: SEQUENCE; Schema: public; Owner: jeebly_db_user
--

CREATE SEQUENCE public.rider_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rider_id_seq OWNER TO jeebly_db_user;

--
-- Name: rider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jeebly_db_user
--

ALTER SEQUENCE public.rider_id_seq OWNED BY public.rider.id;


--
-- Name: riders; Type: TABLE; Schema: public; Owner: jeebly_db_user
--

CREATE TABLE public.riders (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    mobile character varying(10) NOT NULL,
    email character varying(120) NOT NULL,
    vehicle character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    availability character varying(20) NOT NULL,
    date date NOT NULL,
    profile_image character varying(255)
);


ALTER TABLE public.riders OWNER TO jeebly_db_user;

--
-- Name: riders_id_seq; Type: SEQUENCE; Schema: public; Owner: jeebly_db_user
--

CREATE SEQUENCE public.riders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.riders_id_seq OWNER TO jeebly_db_user;

--
-- Name: riders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jeebly_db_user
--

ALTER SEQUENCE public.riders_id_seq OWNED BY public.riders.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: jeebly_db_user
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(120) NOT NULL,
    mobile character varying(10) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public."user" OWNER TO jeebly_db_user;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: jeebly_db_user
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO jeebly_db_user;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jeebly_db_user
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: order id; Type: DEFAULT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: rider id; Type: DEFAULT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.rider ALTER COLUMN id SET DEFAULT nextval('public.rider_id_seq'::regclass);


--
-- Name: riders id; Type: DEFAULT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.riders ALTER COLUMN id SET DEFAULT nextval('public.riders_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: rider rider_pkey; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.rider
    ADD CONSTRAINT rider_pkey PRIMARY KEY (id);


--
-- Name: riders riders_email_key; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.riders
    ADD CONSTRAINT riders_email_key UNIQUE (email);


--
-- Name: riders riders_mobile_key; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.riders
    ADD CONSTRAINT riders_mobile_key UNIQUE (mobile);


--
-- Name: riders riders_pkey; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.riders
    ADD CONSTRAINT riders_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_mobile_key; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_mobile_key UNIQUE (mobile);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: orders orders_rider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jeebly_db_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_rider_id_fkey FOREIGN KEY (rider_id) REFERENCES public.riders(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 2ZZNsWyMvHRhv87SaOkw1lLLa1dUQxljHI8L2AjXUepdvBagYEGmKcgZFCWn9J7


--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Ubuntu 15.1-1.pgdg20.04+1)
-- Dumped by pg_dump version 15.4 (Ubuntu 15.4-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."audit_log_entries" ("instance_id", "id", "payload", "created_at", "ip_address") VALUES
	('00000000-0000-0000-0000-000000000000', 'd711425b-6fc8-413f-90d2-9847b98e9853', '{"action":"user_signedup","actor_id":"00000000-0000-0000-0000-000000000000","actor_username":"service_role","actor_via_sso":false,"log_type":"team","traits":{"user_email":"vinyl@timosur.com","user_id":"2f7a4e06-fc45-4e5f-afdc-cfd93dbc8ddf","user_phone":""}}', '2023-11-27 15:45:08.543647+00', '');


--
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."users" ("instance_id", "id", "aud", "role", "email", "encrypted_password", "email_confirmed_at", "invited_at", "confirmation_token", "confirmation_sent_at", "recovery_token", "recovery_sent_at", "email_change_token_new", "email_change", "email_change_sent_at", "last_sign_in_at", "raw_app_meta_data", "raw_user_meta_data", "is_super_admin", "created_at", "updated_at", "phone", "phone_confirmed_at", "phone_change", "phone_change_token", "phone_change_sent_at", "email_change_token_current", "email_change_confirm_status", "banned_until", "reauthentication_token", "reauthentication_sent_at", "is_sso_user", "deleted_at") VALUES
	('00000000-0000-0000-0000-000000000000', '2f7a4e06-fc45-4e5f-afdc-cfd93dbc8ddf', 'authenticated', 'authenticated', 'vinyl@timosur.com', '$2a$10$aeF7LsEjxyvKTXq3cv.VL.8eFZqkEjZJngxNT75zKYa8HovO6BhLC', '2023-11-27 15:45:08.544833+00', NULL, '', NULL, '', NULL, '', '', NULL, NULL, '{"provider": "email", "providers": ["email"]}', '{}', NULL, '2023-11-27 15:45:08.541495+00', '2023-11-27 15:45:08.544937+00', NULL, NULL, '', '', NULL, '', 0, NULL, '', NULL, false, NULL);


--
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--

INSERT INTO "auth"."identities" ("id", "user_id", "identity_data", "provider", "last_sign_in_at", "created_at", "updated_at") VALUES
	('2f7a4e06-fc45-4e5f-afdc-cfd93dbc8ddf', '2f7a4e06-fc45-4e5f-afdc-cfd93dbc8ddf', '{"sub": "2f7a4e06-fc45-4e5f-afdc-cfd93dbc8ddf", "email": "vinyl@timosur.com"}', 'email', '2023-11-27 15:45:08.542837+00', '2023-11-27 15:45:08.54287+00', '2023-11-27 15:45:08.54287+00');


--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: supabase_auth_admin
--



--
-- Data for Name: key; Type: TABLE DATA; Schema: pgsodium; Owner: supabase_admin
--



--
-- Data for Name: artist; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."artist" ("id", "created_at", "name") VALUES
	(1, '2023-11-27 12:57:53.053308+00', '&me'),
	(2, '2023-11-27 16:22:18.322593+00', 'Adam Beyer & Bart Skils');


--
-- Data for Name: label; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."label" ("id", "created_at", "name") VALUES
	(1, '2023-11-27 13:45:36.717511+00', 'PAMPA'),
	(2, '2023-11-27 16:32:52.721023+00', 'DrumCode');


--
-- Data for Name: record; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."record" ("id", "created_at", "title") VALUES
	(1, '2023-11-27 12:59:12.553766+00', 'In Your Eyes'),
	(2, '2023-11-27 16:36:38.473144+00', 'Your Mind (Charles D Mixes)');


--
-- Data for Name: release; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."release" ("id", "created_at", "name", "record_id", "label_id", "artist_id", "release_date", "price", "delivery_date", "pieces") VALUES
	(1, '2023-11-27 13:45:29.171703+00', 'PAMPA032', 1, 1, 1, '2023-09-08', 12.75, '2023-09-22', 1);


--
-- Data for Name: track; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO "public"."track" ("id", "created_at", "name", "side", "length", "rating", "record_id") VALUES
	(1, '2023-11-27 12:58:28.124725+00', 'In Your Eyes', 'A1', 581, 5, 1),
	(2, '2023-11-27 13:26:18.951345+00', 'As Above So Below', 'B1', 482, 4, 1);


--
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: supabase_storage_admin
--



--
-- Data for Name: hooks; Type: TABLE DATA; Schema: supabase_functions; Owner: supabase_functions_admin
--



--
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: supabase_admin
--



--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: supabase_auth_admin
--

SELECT pg_catalog.setval('"auth"."refresh_tokens_id_seq"', 1, false);


--
-- Name: key_key_id_seq; Type: SEQUENCE SET; Schema: pgsodium; Owner: supabase_admin
--

SELECT pg_catalog.setval('"pgsodium"."key_key_id_seq"', 1, false);


--
-- Name: interpret_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."interpret_id_seq"', 7, true);


--
-- Name: label_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."label_id_seq"', 2, true);


--
-- Name: release_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."release_id_seq"', 1, true);


--
-- Name: track_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."track_id_seq"', 2, true);


--
-- Name: vinyl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('"public"."vinyl_id_seq"', 2, true);


--
-- Name: hooks_id_seq; Type: SEQUENCE SET; Schema: supabase_functions; Owner: supabase_functions_admin
--

SELECT pg_catalog.setval('"supabase_functions"."hooks_id_seq"', 1, false);


--
-- PostgreSQL database dump complete
--

RESET ALL;

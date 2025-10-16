-- SQL INSERT statements for Render deployment
-- Run these in your Render PostgreSQL database
-- Generated on: 2025-10-16 14:54:02

INSERT INTO "user" (id, name, phone_number, password_hash, is_active, created_at, updated_at)
VALUES (1, 'CB', '+17037744294', 'scrypt:32768:8:1$9mFj0FbBulvKQbog$8729ff5f5171357b6e533dac412684db53acb4b88563b38818cc89c691e0ea80b0cd45bad0c5b070d245e6f0a6f8ccbc36ce1a09f817cf10f0b9dbe027c60461', true, '2025-10-15T23:12:34.420749', '2025-10-15T23:14:40.495925');

INSERT INTO "user" (id, name, phone_number, password_hash, is_active, created_at, updated_at)
VALUES (2, 'User 2', '+1234567891', 'scrypt:32768:8:1$ooPWVkCx9c74cCf2$fc0640504cf87e2b0d039369007ef345dfd21e71715e01eabbada40194e8699c31a14928a50017b4cbde4f03524194759bf62c173292ae3f9bb1d7d3c60aa8bb', true, '2025-10-15T23:12:34.467931', '2025-10-15T23:12:34.467934');

INSERT INTO "user" (id, name, phone_number, password_hash, is_active, created_at, updated_at)
VALUES (3, 'User 3', '+1234567892', 'scrypt:32768:8:1$fG1CqBVenA6tTTuB$7ca797773d9981d31b665b4ee56a63f9dbba43f2b99c5ae22b42678e91c1d919c2351f5fde462d0c21546aa0f44b67cc439b05cc49168da7a53643c4cfc8b530', true, '2025-10-15T23:12:34.514149', '2025-10-15T23:12:34.514151');

INSERT INTO "user" (id, name, phone_number, password_hash, is_active, created_at, updated_at)
VALUES (4, 'User 4', '+1234567893', 'scrypt:32768:8:1$ozVgykz9bAGpSthG$7d01da8313d882661371309d3e59e4f31bd942357469809728c945be731f2ae81b99716b8ce49fd22651f8b4a24c67eef3a2293ff7245efc2642e2251659a34a', true, '2025-10-15T23:12:34.561406', '2025-10-15T23:12:34.561408');

-- To run these commands:
-- 1. Go to your Render dashboard
-- 2. Open your PostgreSQL database
-- 3. Go to the 'Shell' tab
-- 4. Paste and run these INSERT statements
-- 5. Or use: psql $DATABASE_URL < users_export.sql

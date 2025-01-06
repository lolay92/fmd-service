CREATE TABLE IF NOT EXISTS ta_vendors (
    id SERIAL PRIMARY KEY,
    vendor TEXT, 
    created_date TIMESTAMPTZ,
    last_updated_date TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ta_exchanges_polygon(
    id SERIAL PRIMARY KEY,
    asset_category TEXT NOT NULL,
    acronym TEXT NOT NULL,
    locale TEXT NOT NULL,
    mic TEXT NOT NULL,
    operatin_mic TEXT NOT NULL,
    participant_id TEXT,
    created_date TIMESTAMPTZ,
    last_updated_date TIMESTAMPTZ
); 

CREATE TABLE IF NOT EXISTS ta_exchanges_eodhd (
    id SERIAL PRIMARY KEY, 
    code_exchange TEXT NOT NULL,
    name_exchange TEXT NOT NULL,
    operating_mic TEXT NOT NULL,
    country TEXT NOT NULL,
    currency TEXT NOT NULL,
    country_iso_2 TEXT,
    country_iso_3 TEXT,
    created_date TIMESTAMPTZ,
    last_updated_date TIMESTAMPTZ
); 

CREATE TABLE IF NOT EXISTS ta_symbols_details (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    company_name TEXT,
    country TEXT,
    mktCap BIGINT,
    currency TEXT,
    cik TEXT, 
    isin TEXT,
    cusip TEXT,
    exchange TEXT,
    industry TEXT,
    sector TEXT, 
    description TEXT,
    ipo_date TEXT,
	isEtf TEXT,
	isActivelyTrading TEXT,
	isAdr  TEXT,
    isFund TEXT
    created_date TIMESTAMPTZ,
    last_updated_date TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS ta_prices_microcaps (
    dt TIMESTAMPTZ NOT NULL,
    symbol_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    adjusted_close DOUBLE PRECISION,
    volume BIGINT,
    vw_avg_price BIGINT,
    transactions_numbr INTEGER,
    PRIMARY KEY (symbol, dt),
    CONSTRAINT fk_symbol_id FOREIGN KEY (symbol_id) REFERENCES ta_symbols_details (id)
); 

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

CREATE INDEX ON ta_prices_microcaps (symbol_id, dt DESC); 

SELECT create_hypertable('ta_prices_microcaps', 'dt'); 



-- -- Numeric Types
-- SMALLINT      -- 2 bytes, -32768 to +32767
-- INTEGER       -- 4 bytes, -2147483648 to +2147483647
-- BIGINT        -- 8 bytes, -9223372036854775808 to +9223372036854775807
-- DECIMAL(p,s)  -- user-specified precision, exact
-- NUMERIC(p,s)  -- user-specified precision, exact
-- REAL          -- 4 bytes, 6 decimal digits precision
-- DOUBLE PRECISION  -- 8 bytes, 15 decimal digits precision
-- SERIAL        -- autoincrementing integer
-- BIGSERIAL     -- autoincrementing bigint

-- -- Character Types
-- CHAR(n)       -- fixed-length, blank padded
-- VARCHAR(n)    -- variable-length with limit
-- TEXT          -- variable unlimited length

-- -- Date/Time Types
-- DATE                    -- date only
-- TIME                    -- time only
-- TIMESTAMP              -- date and time
-- TIMESTAMPTZ            -- date and time with timezone (recommended for TimescaleDB)
-- INTERVAL               -- time interval

-- Boolean Type
-- BOOLEAN       -- true/false

-- Binary Data Types
-- BYTEA         -- binary data ("byte array")

-- Network Address Types
-- CIDR          -- IPv4 and IPv6 networks
-- INET          -- IPv4 and IPv6 hosts and networks
-- MACADDR       -- MAC addresses
## Github actions
-

## Then connect to PostgreSQL with DuckDB
```sql
-- Install the extension once
INSTALL postgres;
LOAD postgres;

-- Attach using your .env credentials
ATTACH 'host=localhost port=5432 dbname=generic_ecommerce_api user=postgres password=password'
    AS pg (TYPE POSTGRES);

SELECT * FROM pg.public.items;

-- List all tables in the database
SELECT table_schema, table_name
    FROM pg.information_schema.tables
    WHERE table_type = 'BASE TABLE'
        AND table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY table_schema, table_name;

-- Use postgres_execute() to run native PostgreSQL DDL (e.g. SERIAL, which DuckDB doesn't support)
CALL postgres_execute('pg', '
    CREATE TABLE test_table (
        row_id SERIAL PRIMARY KEY,
        col1 VARCHAR(255)
    )
');
```

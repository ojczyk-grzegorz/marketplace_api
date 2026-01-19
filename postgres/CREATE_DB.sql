CREATE DATABASE generice_ecommorce_api
	WITH
	OWNER = postgres
	ENCODING = 'UTF-8'
	LOCALE_PROVIDER = 'libc'
	CONNECTION LIMIT = -1
	IS_TEMPLATE = False;

-- SELECT * FROM pg_timezone_names;
ALTER DATABASE generice_ecommorce_api
	SET timezone TO 'UTC';

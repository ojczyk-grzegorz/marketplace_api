CREATE DATABASE generic_ecommerce_api
	WITH
	OWNER = postgres
	ENCODING = 'UTF-8'
	LOCALE_PROVIDER = 'libc'
	CONNECTION LIMIT = -1
	IS_TEMPLATE = False;

ALTER DATABASE generic_ecommerce_api
	SET timezone TO 'UTC';

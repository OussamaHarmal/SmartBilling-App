CREATE TABLE clients(
	id serial PRIMARY KEY,
	full_name VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE,
	adresse text,
	ville VARCHAR(50),
	company_name VARCHAR(100),
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


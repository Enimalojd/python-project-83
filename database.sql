CREATE TABLE IF NOT EXISTS urls (
    id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTYTY,
    name varchar(255) NOT NULL,
    created_at timestamp
);
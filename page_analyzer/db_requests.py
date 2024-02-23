SELECT_ALL_URLS = "SELECT id, name FROM urls ORDER BY id DESC;"
CHECK_FOR_MATCHES = "SELECT id FROM urls WHERE name = (%s);"
ADD_URL = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;"
SELECT_DATA = "SELECT id, name, created_at FROM urls WHERE id = (%s);"

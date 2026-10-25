-- Solo corre la primera vez que se crea el volumen. Base para los tests de integración.
CREATE DATABASE IF NOT EXISTS sigem_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
GRANT ALL PRIVILEGES ON sigem_test.* TO 'sigem'@'%';

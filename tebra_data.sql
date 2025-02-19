CREATE DATABASE tebra_data;
USE tebra_data;

CREATE TABLE providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_name VARCHAR(255),
    company_name VARCHAR(255),
    num_locations INT,
    location_addresses JSON,
    phone_number VARCHAR(50),
    website_link TEXT
);
select * from providers

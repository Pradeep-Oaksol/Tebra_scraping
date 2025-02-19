import json
import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "pradeep",
    "database": "tebra_data"
}

with open("providers_data.json", "r", encoding="utf-8") as file:
    providers_data = json.load(file)

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to MySQL successfully!")

    insert_query = """
    INSERT INTO providers (provider_name, company_name, num_locations, location_addresses, phone_number, website_link)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for provider in providers_data:
        phone_data = json.dumps(provider["Phone Number"]) if isinstance(provider["Phone Number"], list) else provider["Phone Number"]
        location_data = json.dumps(provider["Location Addresses"]) if isinstance(provider["Location Addresses"], list) else provider["Location Addresses"]

        cursor.execute(insert_query, (
            provider["Provider Name"],
            provider["Company Name"],
            provider["Number of Locations"],
            location_data,
            phone_data,
            provider["Website Link"]
        ))

        conn.commit()  # Explicitly commit after each insertion

    print(f"{cursor.rowcount} records inserted successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection closed.")

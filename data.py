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

# If JSON is a dictionary, extract providers from all departments
if isinstance(providers_data, dict):
    all_providers = []
    for dept, providers in providers_data.items():
        if isinstance(providers, list):  # Ensure it's a list of providers
            all_providers.extend(providers)
    providers_data = all_providers  # Replace with flattened list

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    print("Connected to MySQL successfully!")

    insert_query = """
    INSERT INTO providers (provider_name, company_name, num_locations, location_addresses, phone_number, website_link)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for provider in providers_data:
        if not isinstance(provider, dict):  
            print(f"❌ Skipping invalid provider entry: {provider}")
            continue  

        phone_data = provider.get("Phone Number", "N/A")
        if isinstance(phone_data, list):  
            phone_data = json.dumps(phone_data)
        elif isinstance(phone_data, str):
            phone_data = json.dumps([phone_data])
        else:
            phone_data = json.dumps(["N/A"])

        cursor.execute(insert_query, (
            provider.get("Provider Name", "N/A"),
            provider.get("Company Name", "N/A"),
            provider.get("Number of Locations", 0),
            json.dumps(provider.get("Location Addresses", ["N/A"])),
            phone_data,
            provider.get("Website Link", "N/A")
        ))

    conn.commit()
    print(f"{cursor.rowcount} records inserted successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection closed.")

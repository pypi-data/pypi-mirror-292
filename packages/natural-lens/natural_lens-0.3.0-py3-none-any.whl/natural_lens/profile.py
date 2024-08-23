import os
from openai import OpenAI
import pandas as pd
import glob
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def generate_profiles(database_prompt):
    """Generate database table profiles based on CSV files."""
    csv_path = "./data/"
    profiles_path = "./profiles/"
    os.makedirs(csv_path, exist_ok=True)

    csv_files = glob.glob(os.path.join(csv_path, "*.csv"))
    total_files = len(csv_files)
    print(f"Found {total_files} CSV files in {csv_path}.")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_csv_file, file, profiles_path, total_files, index) for index, file in enumerate(csv_files, start=1)]
        for future in as_completed(futures):
            future.result()  # To raise any exceptions that occurred during processing

def process_csv_file(file, profiles_path, total_files, index):
    """Process a CSV file and generate a profile."""
    table_name = os.path.splitext(os.path.basename(file))[0]
    profile_filename = os.path.join(profiles_path, f"{table_name}.md")

    if os.path.exists(profile_filename):
        print(f"Profile for {table_name} already exists. Skipping... {index}/{total_files}")
        return

    data = pd.read_csv(file)
    print(f"Generating profile for {table_name} ({index}/{total_files})...")

    profile = generate_profile(table_name, data)

    os.makedirs(profiles_path, exist_ok=True)
    with open(profile_filename, "w") as f:
        f.write(profile)

    print(f"Profile for {table_name} saved as {profile_filename}. {index}/{total_files} profiles completed.")

def generate_profile(table_name, data, rows=20, database_prompt=""):
    """Generate a detailed profile for a given table."""
    prompt = f"""
    Generate a detailed profile for the table '{table_name}'. The table has the following sample data:
    {data.head(rows).to_string(index=False)}

    Include in the profile:
    - Headline. [# Table {table_name} profile]
    - A summary of the table's purpose based on the data. [## Overview] section
    - An analysis of the most significant columns and what they represent using a table with [name, description, string | number | ..., `sample_data` - some values separated by commas]. (## Columns)
    - Any notable patterns or insights observed from the sample data. [## Insights] section. For this section consider that the data you observe is just a sample, it's not representative of the entire dataset but it provides some shape visibility.
    
    {database_prompt}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in data analysis."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=8192
        )

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred while generating the profile for {table_name}. Error: {e}")
        print("Retrying generating the profile for {table_name} with fewer rows...")
        return generate_profile(table_name, data, int(rows / 2))
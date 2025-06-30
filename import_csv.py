import csv
import requests
import base64
import os
from dotenv import load_dotenv

# --- Configuration! MADE A CHANGE ---
CSV_FILE = "taxonomy_import.csv"  # Your uploaded file
DEFAULT_COLOR = 3
BASE_URL = 'https://josh-anderson.paligoapp.com/api/v2/'
USERNAME = "josh.anderson@paligo.net"

# --- Load API key from environment file ---
load_dotenv("environment.env")
API_KEY = os.getenv("PALIGO_API_KEY")

# --- Encode authentication ---
auth_string = f"{USERNAME}:{API_KEY}"
encoded_auth = base64.b64encode(auth_string.encode()).decode("utf-8")
headers = {
    'Authorization': f'Basic {encoded_auth}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# --- Parse CSV to nested taxonomy tree ---
def parse_csv_to_tree(file_path):
    taxonomy_paths = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for depth, value in enumerate(row):
                value = value.strip()
                if value:
                    if len(taxonomy_paths) == 0 or depth == 0:
                        taxonomy_paths.append([value])
                    else:
                        parent_path = taxonomy_paths[-1][:depth]
                        taxonomy_paths.append(parent_path + [value])
                    break  # Only first non-empty cell

    def build_tree(paths):
        tree = {}
        for path in paths:
            current = tree
            for part in path:
                current = current.setdefault(part, {})
        return tree

    return build_tree(taxonomy_paths)

# --- Recursive taxonomy uploader ---
def create_taxonomy_recursive(tree, parent_id=None):
    for title, children in tree.items():
        body = {
            "title": title,
            "color": DEFAULT_COLOR
        }
        if parent_id:
            body["parent"] = parent_id

        response = requests.post(BASE_URL + "taxonomies/", headers=headers, json=body)
        if response.status_code == 201:
            tax_id = response.json().get("id")
            print(f"✅ Created: {title} (ID: {tax_id})")
            # Recursively create children
            create_taxonomy_recursive(children, parent_id=tax_id)
        else:
            print(f"❌ Failed to create '{title}': {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)

# --- Main execution ---
if __name__ == "__main__":
    tree = parse_csv_to_tree(CSV_FILE)
    create_taxonomy_recursive(tree)

import os
import gspread
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Tuple

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
CSN_DB_ID = os.environ["CSN_DB_ID"]
CHAMEX_DB_ID = os.environ["CHAMEX_DB_ID"]
ADUNICAMP_DB_ID = os.environ["ADUNICAMP_DB_ID"]

notion_dbs = [CSN_DB_ID, CHAMEX_DB_ID, ADUNICAMP_DB_ID]

notion = Client(auth=NOTION_TOKEN)
gc = gspread.service_account(filename="credentials.json")
sheet = gc.open("Burndowntest").sheet1

STATUS_MAP = {
    "Despriorizado": "A fazer",
    "Não iniciado": "A fazer",
    "Aguardando": "Em progresso",
    "Em andamento": "Em progresso",
    "Testando": "Em progresso",
    "Finalizado": "Completo",
    "Aprovado": "Completo"
}

SHEETS_MAP = {
    "CSN | Burndown Chart": CSN_DB_ID,
    "CHAMEX | Burndown Chart": CHAMEX_DB_ID,
    "ADunicamp | Burndown Chart": ADUNICAMP_DB_ID
}

def fetch_notion_tasks(database_id: str) -> List[Tuple[str, str, str, str]]:
    # Query the database
    response = notion.databases.query(database_id=database_id)
    if not response.get("results"):
        print(f"Nenhum resultado encontrado para o banco de dados {database_id}.")
        return []
    tasks = []

    for result in response["results"]:
        props = result["properties"]

        nome = props["Story"]["title"][0]["plain_text"] if props["Story"]["title"] else "Sem nome"
        grupo = props["Estado"]["status"]["name"] if props["Estado"]["status"] else "Sem status"
        status_principal = STATUS_MAP.get(grupo, "Outro")
        data_mov = props["Data"]["date"]["start"] if props.get("Data") and props["Data"].get("date") else "Sem data"

        tasks.append((nome, grupo, status_principal, data_mov))

    return tasks

def get_existing_rows():
    records = sheet.get_all_values()
    return set(tuple(row) for row in records[1:])

def fetch_tasks(databases_ids = List[str]):
    for db_id in databases_ids:
        tasks = fetch_notion_tasks(db_id)
        if tasks:
            return tasks
    return []

def get_sheet_name(database_id: str) -> str:
    for sheet_name, db_id in SHEETS_MAP.items():
        if db_id == database_id:
            return sheet_name
    return None

def update_sheet(tasks):
    existing_rows = get_existing_rows()

    new_rows = [
        list(task)
        for task in tasks
        if tuple(task) not in existing_rows
    ]

    if new_rows:
        for row in new_rows:
            sheet.append_row(row)
        print(f"{len(new_rows)} movimentações novas adicionadas")
    else:
        print("Nenhuma movimentação nova encontrada")
        
def update_all_sheets():
    for sheet_name, db_id in SHEETS_MAP.items():
        tasks = fetch_notion_tasks(db_id)
        if tasks:
            update_sheet(tasks)
        else:
            print(f"Nenhuma tarefa encontrada para {sheet_name}")

if __name__ == "__main__":
    tasks = fetch_tasks(notion_dbs)
    if not tasks:
        print("Nenhuma tarefa encontrada")
    else:
        update_all_sheets()
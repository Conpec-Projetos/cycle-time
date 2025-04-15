import os
import gspread
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

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

def fetch_tasks():
    response = notion.databases.query(database_id=NOTION_DATABASE_ID)
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
        print(f"{len(new_rows)} movimentações novas adicionadas.")
    else:
        print("Nenhuma movimentação nova encontrada.")

if __name__ == "__main__":
    tasks = fetch_tasks()
    update_sheet(tasks)
    print("Burndown sincronizado com sucesso 🧨📉")
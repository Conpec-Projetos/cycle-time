import os
import gspread
from notion_client import Client
from typing import List, Tuple
import pandas as pd
import json
# from dotenv import load_dotenv
# load_dotenv()

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
CREDENTIALS_JSON = os.environ["CREDENTIALS_JSON"]
CSN_DB_ID = os.environ["CSN_DB_ID"]
ADUNICAMP_DB_ID = os.environ["ADUNICAMP_DB_ID"]
MEU_APE_DB_ID = os.environ["MEU_APE_DB_ID"]
SOCIAL_MENTES_DB_ID = os.environ["SOCIAL_MENTES_DB_ID"]
CHAMEX_DB_ID = os.environ["CHAMEX_DB_ID"]

notion = Client(auth=NOTION_TOKEN)
credentials_dict = json.loads(CREDENTIALS_JSON)
gc = gspread.service_account_from_dict(credentials_dict)

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
    "CSN | Data": CSN_DB_ID,
    "ADunicamp | Data": ADUNICAMP_DB_ID,
    "Meu Apê | Data": MEU_APE_DB_ID,
    "Social Mentes | Data": SOCIAL_MENTES_DB_ID,
    "Chamex | Data": CHAMEX_DB_ID
}

def fetch_notion_tasks(database_id: str) -> List[Tuple[str, str, str, str]]:
    response = notion.databases.query(database_id=database_id)
    if not response.get("results"):
        print(f"Nenhum resultado encontrado para o banco de dados {database_id}.")
        return []
    tasks = []

    for result in response["results"]:
        props = result["properties"]

        nome = props["Story"]["title"][0]["plain_text"] if props["Story"]["title"] else "Sem nome"
        grupo = props["Estado"]["status"]["name"] if (props["Estado"]["status"] or props["Status"]['status']) else "Sem status"
        status_principal = STATUS_MAP.get(grupo, "Outro")
        data_mov = props["DateChange"]["date"]["start"] if props.get("DateChange") and props["DateChange"].get("date") else "Sem data"

        tasks.append((nome, grupo, status_principal, data_mov))

    tasks = [task for task in tasks if task[3] != "Sem data"]
    return tasks

def get_existing_rows(sheet) -> List[Tuple[str, str, str, str]]:
    records = sheet.get_all_values()
    return set(tuple(row) for row in records[0:])

def update_sheet(tasks, sheet_name: str):
    sheet = gc.open(sheet_name).sheet1
    existing_rows = get_existing_rows(sheet)

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
        print(f"Nenhuma movimentação nova encontrada em {sheet_name[0:-6]}")
        
def update_all_sheets():
    for sheet_name, db_id in SHEETS_MAP.items():
        tasks = fetch_notion_tasks(db_id)
        if tasks:
            update_sheet(tasks, sheet_name)
        else:
            print(f"Nenhuma tarefa encontrada para {sheet_name}")
            
def calculate_cycle_times(sheet_name: str) -> pd.DataFrame:
    sheet = gc.open(sheet_name).sheet1
    values = sheet.get_all_values()

    columns = ['Tarefa', 'Status Secundário', 'Status Principal', 'Data Movimentação']
    df = pd.DataFrame(values, columns=columns)

    df['Data Movimentação'] = pd.to_datetime(df['Data Movimentação'], errors='coerce')

    grouped = df.groupby(['Tarefa', 'Status Principal'])

    started = grouped['Data Movimentação'].min().unstack()

    if started.get('Em progresso') is None or started.get('Completo') is None:
        print(f"Planilha '{sheet_name}' não contém items 'Em progresso' ou 'Completo'.")
        return pd.DataFrame(columns=['Tarefa', 'Cycle Time (dias)'])
    started['Cycle Time (dias)'] = (
        started.get('Completo') - started.get('Em progresso')
    ).dt.days

    result_df = started.reset_index()[['Tarefa', 'Cycle Time (dias)']]

    return result_df

def calculate_global_cycle_time(sheet_names: List[str]) -> float:
    all_cycle_times = []

    for sheet_name in sheet_names:
        cycle_df = calculate_cycle_times(sheet_name)

        project_cycle_times = cycle_df['Cycle Time (dias)'].dropna().tolist()
        if not project_cycle_times:
            print(f"Nenhum cycle time encontrado para o projeto {sheet_name}.")
            continue
        
        project_sheet = gc.open(sheet_name).worksheet("Cycle Time")

        last_row = len(project_sheet.get_all_values()) + 1
        project_sheet.update_cell(last_row, 1, round(sum(project_cycle_times) / len(project_cycle_times), 2))
        project_sheet.update_cell(last_row, 2, pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')) 
        
        all_cycle_times.extend(project_cycle_times)

    if all_cycle_times:
        global_average = sum(all_cycle_times) / len(all_cycle_times)
        return round(global_average, 2)
    else:
        print("Nenhum cycle time encontrado para os projetos.")
        return 0.0
    
def update_cycle_time_in_okrs_sheet():
    okrs_sheet = gc.open("0. [Conpec][2025] Painel Estratégico de 2025").worksheet("Dashboard")
    cycle_time = calculate_global_cycle_time(list(SHEETS_MAP.keys()))
    print(f"Ciclo médio de tempo: {cycle_time} dias")
    okrs_sheet.update([[cycle_time]], range_name="G21")

if __name__ == "__main__":
    update_all_sheets()
    update_cycle_time_in_okrs_sheet()
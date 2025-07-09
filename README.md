# Cycle Time Tracking System

A Python application that integrates with Notion databases and Google Sheets to track and calculate cycle times for project management tasks. This system automatically fetches task data from Notion, processes it, and updates Google Sheets with cycle time metrics.

## Project Structure

```text
cycle-time/
├── .env                 # Where you'll store all your environment variables (not included in repo)
├── main.py              # Main application logic
├── requirements.txt     # Python dependencies
└── credentials.json     # Decrypted credentials (given by the user, not included in repo)
```

## Prerequisites

- Python 3.7+
- Access to Notion API
- Google Sheets API access
- Google service account credentials

## Features

- **Notion Integration**: Fetches task data from multiple Notion databases
- **Google Sheets Integration**: Updates Google Sheets with task movements and cycle time calculations
- **Automated Cycle Time Calculation**: Calculates cycle times based on task status transitions

## How It Works

1. **Data Extraction**: Fetches tasks from Notion databases, including task names, statuses, and movement dates
2. **Status Standardization**: Maps various status names to three main categories:
   - `A fazer` (To Do)
   - `Em progresso` (In Progress)
   - `Completo` (Complete)
3. **Sheet Updates**: Adds new task movements to corresponding Google Sheets
4. **Cycle Time Calculation**: Calculates the time between "Em progresso" and "Completo" statuses
5. **Dashboard Updates**: Updates Conpec's PE, a central strategic dashboard, with global cycle time metrics

## Status Mapping

The system maps various Notion statuses to standardized workflow stages:

| Notion Status | Mapped Status |
| ------------- | ------------- |
| Despriorizado | A fazer       |
| Não iniciado | A fazer       |
| Aguardando    | Em progresso  |
| Em andamento  | Em progresso  |
| Testando      | Em progresso  |
| Finalizado    | Completo      |
| Aprovado      | Completo      |

---

## Configuration

### Dependencies

To Install dependencies, run:

```bash
pip install -r requirements.txt
```

### Environment Variables

Set the following environment variables:

```bash
NOTION_TOKEN=your_notion_integration_token
ENCRYPTION_KEY=your_encryption_key_for_credentials
```

### Adding New Projects

1. To add a new project, you have to get the Notion backlog database IDs. To get them, you have to open the projects in Notion on your browser, go to their "Backlog pages" and copy the database ID from the URL. The ID is the part after `https://www.notion.so/` and before the question mark or any other parameters.

   Here's an example of how the URL looks like, where the database ID in this case is `1234567890abcdef1234567890abcdef`:

   ```bash
   https://www.notion.so/1234567890abcdef1234567890abcdef?v=0987654321zyxwvutsrqponmlkj
   ```

   Finally, after having all the desired IDs, go to the environment variables file and add them as follows:

   ```bash
   YOUR_PROJECT_DB_ID=your_project_notion_database_id
   YOUR_PROJECT_2_DB_ID=your_project_2_notion_database_id
   ```
2. Then, update the `SHEETS_MAP` dictionary in `main.py`. The key should be the name of the sheet created by you in Google Sheets and stored in the Conpec Google Drive, and the value should be the Notion database ID for that project.

   ```python
   SHEETS_MAP = {
      "Your Project Name | Data": YOUR_PROJECT_DB_ID,
      # ... other projects
   }
   ```
3. Afterwards update the `github/workflows/sync.yml` file by adding the name of the environment variable you set:

   ```yaml
   - name: Decrypt and run
     env:
       ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
       NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
       YOUR_PROJECT_DB_ID: ${{ secrets.YOUR_PROJECT_DB_ID }}
       YOUR_PROJECT_2_DB_ID: ${{ secrets.YOUR_PROJECT_2_DB_ID }}
   ```
4. And last but not least, add all these environment variables in the GitHub "Secrets and Variables" section of this project.

### Credentials

Add your `credentials.json` file to the project root directory. This file should contain your Google service account credentials in JSON format to access Google Sheets.

## Usage

Run the main script to update all sheets and calculate cycle times:

```bash
python main.py
```

## Troubleshooting

- Ensure all environment variables are set correctly
- Verify that your Notion integration has access to the required databases (Connections option from the 3 dots in the header)
- Check that your Google service account has access to the target spreadsheets

## License

This project is for internal use at Conpec.

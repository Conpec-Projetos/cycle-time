# Cycle Time Tracking System

A Python application that integrates with Notion databases and Google Sheets to track and calculate cycle times for project management tasks. This system automatically fetches task data from Notion, processes it, and updates Google Sheets with cycle time metrics.

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
|---------------|---------------|
| Despriorizado | A fazer |
| Não iniciado | A fazer |
| Aguardando | Em progresso |
| Em andamento | Em progresso |
| Testando | Em progresso |
| Finalizado | Completo |
| Aprovado | Completo |

## Project Structure

```text
cycle-time/
├── main.py              # Main application logic
├── decrypt.py           # Credential decryption utility
├── requirements.txt     # Python dependencies
├── credentials.json.enc # Encrypted Google service account credentials
└── credentials.json     # Decrypted credentials (given by the user, not included in repo)
```

## Prerequisites

- Python 3.7+
- Access to Notion API
- Google Sheets API access
- Google service account credentials
- OpenSSL (for credential decryption)

## Environment Variables

Set the following environment variables:

```bash
NOTION_TOKEN=your_notion_integration_token
CSN_DB_ID=your_csn_notion_database_id
ADUNICAMP_DB_ID=your_adunicamp_notion_database_id
ENCRYPTION_KEY=your_encryption_key_for_credentials
```

If you have more projects, you can add their Notion database IDs to the environment variables as needed. To get the ids, you have to open the projects in Notion on your browser, go to their "Backlog pages" and copy the database ID from the URL. The ID is the part after `https://www.notion.so/` and before the question mark or any other parameters.

Here's an example of how the URL looks like:

```bash
https://www.notion.so/1234567890abcdef1234567890abcdef?v=0987654321zyxwvutsrqponmlkj
```

The database ID in this case is `1234567890abcdef1234567890abcdef`.

## Installation and Setup

To set up the Cycle Time Tracking System, follow these steps:

1. Clone this repository

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables

4. Add your `credentials.json` file to the project root directory. This file should contain your Google service account credentials in JSON format to access Google Sheets.

5. Encrypt your credentials file using the provided `decrypt.py` script:

   ```bash
   python decrypt.py
   ```

   This will create an encrypted version of your credentials file named `credentials.json.enc`. Make sure to keep your original `credentials.json` file secure and not included in the repository.

## Usage

### Basic Usage

Run the main script to update all sheets and calculate cycle times:

```bash
python main.py
```

This will:

1. Fetch latest data from all configured Notion databases
2. Update corresponding Google Sheets with new task movements
3. Calculate cycle times for all projects
4. Update the PE dashboard with global metrics

## Configuration

### Adding New Projects

To add a new project, update the `SHEETS_MAP` dictionary in `main.py`:

```python
SHEETS_MAP = {
    "Your Project Name | Data": "your_notion_database_id",
    # ... other projects
}
```

The key should be the name of the sheet created by you in Google Sheets and stored in the Conpec Google Drive, and the value should be the Notion database ID for that project.

### Creating New Sheets

To create a new Google Sheet for a project, follow these steps:

1. Create a new Google Sheet in your Google Drive.
2. Share it with your Google service account email.
3. Add the new sheet's ID to the `SHEETS_MAP` in `main.py`:

```python
SHEETS_MAP = {
    "New Project Name | Data": "new_notion_database_id",
    # ... other projects
}
```

## Troubleshooting

- Ensure all environment variables are set correctly
- Verify that your Notion integration has access to the required databases
- Check that your Google service account has access to the target spreadsheets
- Make sure OpenSSL is available in your system PATH for credential decryption

## License

This project is for internal use at Conpec.

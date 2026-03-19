import os
import json
import base64
import logging
import requests
from datetime import datetime, date, timedelta
from flask import Flask, jsonify, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from apscheduler.schedulers.background import BackgroundScheduler
from io import BytesIO
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

BLING_API_KEY = os.getenv("BLING_API_KEY")
GOOGLE_DRIVE_ROOT_FOLDER = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER", "F&R Contabilidade")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

def get_drive_service():
    try:
        creds_json = GOOGLE_CREDENTIALS_JSON
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON nao configurada")
        try:
            creds_info = json.loads(base64.b64decode(creds_json).decode('utf-8'))
        except Exception:
            creds_info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_info, scopes=['https://www.googleapis.com/auth/drive.file'])
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        logger.error(f"Erro ao autenticar no Google Drive: {e}")
        return None

def find_or_create_folder(service, folder_name, parent_id=None):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    if files:
        return files[0]['id']
    file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def upload_to_drive(service, file_name, content, parent_id, mime_type='application/pdf'):
    file_metadata = {'name': file_name, 'parents': [parent_id]}
    media = MediaIoBaseUpload(BytesIO(content), mimetype=mime_type)
    return service.files().create(body=file_metadata, media_body=media, fields='id').execute().get('id')

def get_bling_nfe(api_key, tipo):
    hoje = date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_passado = primeiro_dia_mes_atual - timedelta(days=1)
    primeiro_dia_mes_passado = ultimo_dia_mes_passado.replace(day=1)
    data_inicial = primeiro_dia_mes_passado.strftime("%Y-%m-%d")
    data_final = ultimo_dia_mes_passado.strftime("%Y-%m-%d")
    url = "https://api.bling.com.br/Api/v3/nfe"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"dataEmissaoInicial": data_inicial, "dataEmissaoFinal": data_final, "tipo": tipo, "limite": 100}
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        return []

def download_nfe_pdf(api_key, nfe_id):
    url = f"https://api.bling.com.br/Api/v3/nfe/{nfe_id}/danfe"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/pdf"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None

def sync_job():
    drive_service = get_drive_service()
    if not drive_service:
        return {"error": "Falha Drive"}
    root_id = find_or_create_folder(drive_service, GOOGLE_DRIVE_ROOT_FOLDER)
    f_in = find_or_create_folder(drive_service, "Notas-Entrada", root_id)
    f_out = find_or_create_folder(drive_service, "Notas-Saida", root_id)
    res = {"entrada": 0, "saida": 0}
    for n in get_bling_nfe(BLING_API_KEY, 1):
        pdf = download_nfe_pdf(BLING_API_KEY, n['id'])
        if pdf:
            upload_to_drive(drive_service, f"NFe_{n['numero']}_{n['dataEmissao']}.pdf", pdf, f_out)
            res["saida"] += 1
    for n in get_bling_nfe(BLING_API_KEY, 0):
        pdf = download_nfe_pdf(BLING_API_KEY, n['id'])
        if pdf:
            upload_to_drive(drive_service, f"NFe_Entrada_{n['numero']}_{n['dataEmissao']}.pdf", pdf, f_in)
            res["entrada"] += 1
    return res

scheduler = BackgroundScheduler()
scheduler.add_job(sync_job, 'cron', day=1, hour=8, minute=0)
scheduler.start()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

@app.route('/sync-now', methods=['POST', 'GET'])
def sync_now():
    return jsonify(sync_job())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

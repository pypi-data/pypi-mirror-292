import re
import requests
import os
from urllib.parse import quote

def get_sheet_id(url_or_id):
    """從 URL 或 ID 字符串中提取 Google Sheets ID"""
    if '/' not in url_or_id:
        return url_or_id
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url_or_id)
    return match.group(1) if match else url_or_id

def get_spreadsheet_info(sheet_id):
    """獲取 Google Sheet 中所有工作表的名稱和 GID"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    result = {
        "status": False,
        "error": [],
        "data": {}
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        # Extract sheet names
        sheet_names = re.findall(r'docs-sheet-tab-caption[^>]+>([^<]+)</div>', html_content)

        # Extract mergedConfig
        config_match = re.search(r'var bootstrapData\s*=\s*({.*?});', html_content, re.DOTALL)
        if config_match:
            config_str = config_match.group(1)
            try:
                for index, sheet_name in enumerate(sheet_names):
                    begin_pattern = f'[{index},0,\\"'
                    end_pattern = f'\\",['
                    begin_index = config_str.find(begin_pattern)
                    end_index = config_str.find(end_pattern, begin_index)
                    gid_value = config_str[begin_index + len(begin_pattern):end_index]
                    result["data"][sheet_name] = gid_value
                result["status"] = True
            except Exception as e:
                result["error"].append(f"Error extracting sheet information: {str(e)}")
        else:
            result["error"].append("Could not find bootstrapData in the HTML content")
    except requests.RequestException as e:
        result["error"].append(f"Error fetching the spreadsheet: {str(e)}")
    
    return result

def get_sheet_data(sheet_id, sheet_name, gid, file_format='csv'):
    """獲取指定 Google Sheet 的數據"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format={file_format}&gid={gid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def export_sheet(sheet_id, sheet_name, gid, output_dir, file_format='csv'):
    """導出單個工作表"""
    data = get_sheet_data(sheet_id, sheet_name, gid, file_format)
    file_name = f"{sheet_name}.{file_format}"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'wb') as f:
        f.write(data)
    
    print(f"[INFO] Exported {file_name}")

def backup_sheets(url_or_id, output_dir, file_format='csv'):
    """備份整個 Google Sheets 文檔"""
    sheet_id = get_sheet_id(url_or_id)
    sheet_info = get_spreadsheet_info(sheet_id)
    
    if not sheet_info["status"]:
        for error in sheet_info["error"]:
            print(f"[ERROR] {error}")
        return

    if not sheet_info["data"]:
        print("[ERROR] No sheets found in the spreadsheet")
        return

    for sheet_name, gid in sheet_info["data"].items():
        try:
            export_sheet(sheet_id, sheet_name, gid, output_dir, file_format)
        except Exception as e:
            print(f"[ERROR] Error exporting sheet '{sheet_name}': {str(e)}")

def export_sheets_csv(url_or_id, output_dir):
    """將 Google Sheets 導出為 CSV 格式"""
    backup_sheets(url_or_id, output_dir, 'csv')

def export_sheets_tsv(url_or_id, output_dir):
    """將 Google Sheets 導出為 TSV 格式"""
    backup_sheets(url_or_id, output_dir, 'tsv')

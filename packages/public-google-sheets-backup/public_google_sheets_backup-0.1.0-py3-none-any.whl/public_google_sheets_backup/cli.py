import argparse
import os
import sys
from . import __version__
from .core import backup_sheets, export_sheets_csv, export_sheets_tsv

def main():
    parser = argparse.ArgumentParser(description="Backup or export public Google Sheets")
    parser.add_argument("url_or_id", help="URL or ID of the Google Sheet")
    parser.add_argument("-o", "--output", default="./output-gsheets", help="Output directory (default: ./output-gsheets)")
    parser.add_argument("--type", choices=['csv', 'tsv'], default='csv', help="Export type (default: csv)")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    if len(sys.argv) == 1:
        print(f"public_google_sheets_backup version {__version__}")
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)

    print(f"public_google_sheets_backup version {__version__}")
    print(f"Exporting {args.url_or_id} as {args.type} to {args.output}")
    
    backup_sheets(args.url_or_id, args.output, args.type)

def csv_export():
    parser = argparse.ArgumentParser(description="Export public Google Sheets as CSV")
    parser.add_argument("url_or_id", help="URL or ID of the Google Sheet")
    parser.add_argument("-o", "--output", default="./output-gsheets", help="Output directory (default: ./output-gsheets)")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)

    print(f"public_google_sheets_backup version {__version__}")
    print(f"Exporting {args.url_or_id} as CSV to {args.output}")
    
    export_sheets_csv(args.url_or_id, args.output)

def tsv_export():
    parser = argparse.ArgumentParser(description="Export public Google Sheets as TSV")
    parser.add_argument("url_or_id", help="URL or ID of the Google Sheet")
    parser.add_argument("-o", "--output", default="./output-gsheets", help="Output directory (default: ./output-gsheets)")
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output, exist_ok=True)

    print(f"public_google_sheets_backup version {__version__}")
    print(f"Exporting {args.url_or_id} as TSV to {args.output}")
    
    export_sheets_tsv(args.url_or_id, args.output)

if __name__ == "__main__":
    main()

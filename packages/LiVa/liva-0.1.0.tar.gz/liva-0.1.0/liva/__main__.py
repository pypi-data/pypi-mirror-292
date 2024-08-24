import re
import requests
import pandas as pd
import pretty_errors

import rich
from rich.table import Table
from pathlib import Path
from argparse import ArgumentParser
from rich_argparse import RichHelpFormatter
from tabulate import tabulate

HTTP_ERRORCODES = [400, 404]

def parse_arguments():
    parser = ArgumentParser(
        description='Check external links in files.',
        formatter_class=RichHelpFormatter
    )

    parser.add_argument(
        "--directory", "-d",
        type=str,
        default=".",
        help="The directory to start scanning from."
    )
    
    parser.add_argument(
        "--only-failure",
        action="store_true",
        help="Only display URLs that resulted in a failure status code."
    )
    
    parser.add_argument(
        "--show-reason",
        action="store_false",
        help="Display HTTPS-Response-Reason."
    )
    
    parser.add_argument(
        "--errorcodes", "-e",
        action='append',
        help="Errorcodes which are causing exit-status: 1 (failure)"
    )

    cli_args = parser.parse_args()
    return cli_args

def main():
    cli_args = parse_arguments()
    
    # Pfad zum Projektverzeichnis
    project_dir = Path(cli_args.directory)
    
    data = []
    for md_file in project_dir.rglob("*.md"):
        data += [result for result in check_files_for_urls(md_file)]

    columns=["source", "url", "statuscode", "reason"]
    df = pd.DataFrame(columns=columns, data=data)

    visualize_results(df, only_failure=cli_args.only_failure, show_reason=cli_args.show_reason)
    evaluate_results(df, cli_args.errorcodes, HTTP_ERRORCODES)
    

def evaluate_results(df, user_errorcodes, default_errorcodes):
    if user_errorcodes:
        errorcodes = user_errorcodes + default_errorcodes
    else: 
        errorcodes = default_errorcodes

    if df['statuscode'].isin(errorcodes).any() or df['statuscode'].isnull().any():
        exit(1)
    else:
        exit(0)


def visualize_results(df, only_failure=False, show_reason=False):

    if show_reason:
        df = df.drop(columns=["reason"])
    if only_failure:
        df = df[(df['statuscode'] < 200) | (df['statuscode'] >= 300) | df['statuscode'].isna()]

    table = Table(title="Overview of outgoing-urls:")
    for col in df.columns:
        table.add_column(col)

    numerical_column = 'statuscode'
    for i, row in df.iterrows():
        colored_row = []
        for col in df.columns:
            val = row[col]
                
            if col == numerical_column:
                if val < 200:
                    colored_row.append(f"[blue]{val}[blue]")
                elif val >= 200 and val < 300:
                    colored_row.append(f"[green]{val}[green]")
                elif val >= 300 and val < 400:
                    colored_row.append(f"[white]{val}[white]")
                elif val >= 400 and val < 500:
                    colored_row.append(f"[bold red]{val}[/bold red]")
                elif val >= 500:
                    colored_row.append(f"[bold orange]{val}[/bold orange]")
                else:
                    colored_row.append("[red]None[red]")
            else:
                colored_row.append(str(val))

        table.add_row(*colored_row)
    rich.print(table)


def check_files_for_urls(file):
    # regexp for all possible urls ...
    link_pattern = re.compile(r'\b[a-zA-Z][a-zA-Z0-9+.-]*:\/\/[^\s/$.?#].[^\s]*\b') 

    with open(file, "r", encoding="utf-8") as file:
        content = file.read()
        links = link_pattern.findall(content)
        for link in links:
            statuscode, reason = check_url(link)

            if statuscode:
                data = [file.name, link, statuscode, reason]
            else:
                data = [file.name, link, None, None]
            yield data


def check_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code, response.reason
    except requests.RequestException as e:
        return None


if __name__=="__main__":
    main()
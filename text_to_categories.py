from categories_dict import name_to_categories_dict
import pandas as pd
import os
import numpy as np
from tabulate import tabulate

banking_file_csv = r'Umsaetze_Beispiel.csv'

def df_from_csv(csv_filepath:str, sep=';', encoding='utf-8-sig', 
                decimal= ',', thousands = '.', dtype=None):
    df = pd.read_csv(
        csv_filepath,
        sep=sep,
        encoding=encoding,
        decimal=decimal,
        thousands=thousands,
        dtype=dtype
    )

    return df

def rename_df(df: pd.DataFrame, col_names, col_ind_list=None):
    if col_ind_list is None:
        for col_ind in range(len(col_names)):
            df = df.rename(columns={df.columns[col_ind]:col_names[col_ind]} )
    elif len(col_names) == len(col_ind_list):
        for i, col_ind in enumerate(col_ind_list):
            df = df.rename(columns={df.columns[col_ind]:col_names[i]} )
    else:
        raise ValueError('Number of column names and number of given column indices have to be the same size')

    return df

def get_category_of_name(category_dict: dict, name: str, zweck: str):
    category_key = [key for key in category_dict.keys() if key.lower() in name.lower()]
    
    if category_key:
        return category_dict[category_key[0]]
    else:
        category_key = [key for key in category_dict.keys() if key.lower() in zweck.lower()]
        if category_key:
            return category_dict[category_key[0]]

    return 'Sonstiges'

def get_overview_df(df: pd.DataFrame):
    df_overview = pd.pivot_table(df, values='Betrag', index='Kategorie', columns='Monat', aggfunc='sum', sort=False, fill_value=0)

    # Inverse order of columns such that months are from earliest to latest
    df_overview = df_overview.iloc[:, ::-1]

    # Append sum row and mean column at end of table
    df_overview.loc['Sum'] = df_overview.sum()
    df_overview.loc[:, 'Mean'] = df_overview.mean(axis=1)
    
    return df_overview

def pretty_table(df: pd.DataFrame, headers='keys', tablefmt='psql', showindex=True):
    return tabulate(df, headers=headers, tablefmt=tablefmt, showindex=showindex)

def save_prettytable_to_textfile(df: pd.DataFrame, path: str, overwrite=False, headers='keys', tablefmt='psql', showindex=True):
    if not overwrite and os.path.exists(path):
        print("File exists already. If you want to overwrite it execute the function with overwrite=True")
        return
    
    df_pretty = pretty_table(df, headers=headers, tablefmt=tablefmt, showindex=showindex)
    with open(path, 'w') as f:
        f.write(df_pretty)

if __name__ == '__main__':
    # Erhalte pandas df von einer csv Datei
    df = df_from_csv(banking_file_csv, dtype={'Buchungstag': str})

    # Benenne Spaltennamen um
    df = rename_df(df, ['Datum', 'Name', 'Zweck', 'Betrag'])

    # Behalte nur das Datum der 'Datum'-Spalte und ergänze eine Monatsspalte
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y').dt.date 
    df['Monat'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d').dt.strftime('%b-%y')

    # Erstelle neue Kategorie Spalte
    df['Kategorie'] = ''

    print(df)

    # Ergänze Kategorie in jeder Zeile in Abhängigkeit vom Namen
    # for i, name in enumerate(df['Name']):
    for i in range(df.shape[0]):
        name = df['Name'].iloc[i]
        zweck = df['Zweck'].iloc[i]
        df['Kategorie'].iat[i] = get_category_of_name(name_to_categories_dict, name=name, zweck=zweck)

    # Monatsübersicht erstellen
    df_overview = get_overview_df(df)

    # Tabelle auf der Konsole ausgeben
    print(pretty_table(df_overview))

    # Pretty Tabelle als Textdatei speichern 
    save_prettytable_to_textfile(df_overview, os.path.join('tables', "example_table_overview.txt"), overwrite=False)
    
    # Pretty Tabelle per Monat als Textdatei speichern 
    for month in df_overview.columns[:-1]:  # Exclude 'Mean' columns
        df_month = df[df['Monat']==month]
        df_month['Zweck'] = df_month['Zweck'].apply(lambda x: (x[:26] + '...') if len(x) > 26 else x)
        save_prettytable_to_textfile(df_month, os.path.join('tables', f"example_table_{month}.txt"), overwrite=False, showindex=False)

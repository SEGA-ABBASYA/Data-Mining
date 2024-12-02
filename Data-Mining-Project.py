import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd

# Can be taken as input from the GUI later on
minimum_support = 2
minimum_confidence = 2

transactions_file_path = 'transactions.xlsx'
transactions_excel = pd.read_excel(transactions_file_path)

transactions_hash_table = {}

# Transform excel input into a horizontal format hash table <TID, Items>
for _, row in transactions_excel.iterrows():
    key = row['TiD'] 
    value = row['items'].split(',')
    transactions_hash_table[key] = value
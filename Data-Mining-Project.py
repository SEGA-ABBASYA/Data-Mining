import string
from collections import defaultdict

import pandas as pd

import tkinter as tk
from tkinter import ttk, filedialog

# IMPORTANT: Can be taken as input from the GUI later on
minimum_support = 2
minimum_confidence = 2

transactions_excel_file_path = 'transactions.xlsx'
transactions_excel = pd.read_excel(transactions_excel_file_path)

transactions = {}

# Transform excel input into a transactions hash table <TID, Items>
for _, row in transactions_excel.iterrows():
    key = row['TiD'] 
    value = row['items'].split(',')
    transactions[key] = value

# Creates a one itemsets hash table <Item, Support Count>
# Sets the default support count for any new item to 0
one_itemsets_support_count = defaultdict(int)

# Count support counts for all items
for letter in string.ascii_uppercase:
    for items in transactions.values():
        if letter in items:
            one_itemsets_support_count[letter] += 1

# Remove (prune) items with support count less than minimum support count
for item, support_count in one_itemsets_support_count.items():
    if support_count < minimum_support:
        for items in transactions.values():
            if item in items:
                items.remove(item)

# Sorts the one itemsets descendingly based on the support count
one_itemsets_support_count = dict(sorted(one_itemsets_support_count.items(), key=lambda x: x[1], reverse=True))

items_ordering = {char: idx for idx, char in enumerate(one_itemsets_support_count.keys())}

# Sort items in the transactions based on the ordering in one_itemsets_support_count
for key, value in transactions.items():
    transactions[key] = sorted(value, key=lambda x: items_ordering.get(x))
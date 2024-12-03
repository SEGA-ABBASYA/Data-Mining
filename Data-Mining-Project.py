import string
from collections import defaultdict

import pandas as pd

import tkinter as tk
from tkinter import ttk, filedialog

# IMPORTANT: Can be taken as input from the GUI later on
minimum_support = 2
minimum_confidence = 2

transactions_excel_file_path = 'transactions1.xlsx'
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

class Node:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency
        # List of child nodes
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    # Specifies how to represent/print the object
    def __repr__(self):
        return f"Node: {self.name}, Frequency: {self.frequency}"

# Root of the FP growth tree
null_node = Node('null', 0)

# Construct the FP growth tree using the sorted transactions' items
for items in transactions.values():
    current_node = null_node

    for item in items:
        item_in_children = 0
        for child in current_node.children:
            if child.name == item:
                child.frequency += 1
                item_in_children = 1
                current_node = child
                break
        
        if not item_in_children:
            new_child = Node(item, 1)
            current_node.add_child(new_child)
            current_node = new_child
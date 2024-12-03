import string
from collections import defaultdict
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import Canvas
# IMPORTANT: Can be taken as input from the GUI later on
minimum_support = 3
minimum_confidence = 0.2

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
null_node = Node('null',0)

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

#list for storing the currently hold items in the dfs function
current_items = []
#2D dict for storing the freq of each item with a certain item
conditional_pattern = {row: {col: 0 for col in one_itemsets_support_count.keys()} for row in one_itemsets_support_count.keys()}
#dfs function which counts the freq of each item according to a certain item (ex: conditional_patten['Y']['X'] : 3)
def dfs(node):
    for item in current_items:
        conditional_pattern[node.name][item] += node.frequency
    if node != null_node:
        current_items.append(node.name)
    for child in node.children:
        dfs(child)
    if node != null_node:
        current_items.pop()

#Calling the dfs function
dfs(null_node)
#item set that has each size with it each itemset
frequnt_itemset = [[] for _ in range(len(one_itemsets_support_count.keys()))]
for item in one_itemsets_support_count.keys():
    if one_itemsets_support_count[item] >= minimum_support:
        frequnt_itemset[1].append([item])

#list to calculate each combination in
current_items_to_add = []

#recursive take or leave function
def count(index):
    if index == len(current_items):
        if len(current_items_to_add) > 1:
            frequnt_itemset[len(current_items_to_add)].append(current_items_to_add.copy())
        return
    current_items_to_add.append(current_items[index])
    count(index+1)
    current_items_to_add.pop()
    count(index+1)

for item1 in conditional_pattern.keys():
    for item2 in conditional_pattern[item1].keys():
        if conditional_pattern[item1][item2] >= minimum_support:
            current_items.append(item2)
    current_items_to_add.append(item1)
    count(0)
    current_items_to_add.pop()
    current_items.clear()

#count the support for a given item set
def count_itemset_support(itemset, transactions):
    sup_count = 0
    for transactions_items in transactions.values():
        all_exist = True
        for item in itemset:
            found = False
            for transactions_item in transactions_items:
                if item == transactions_item:
                    found = True
                    break
            if not found:
                all_exist = False
                break
        if all_exist:
            sup_count += 1
    return sup_count

#generate subsets of an itemset
def generate_subsets(itemset, index, current_subset, all_subsets):

    if index == len(itemset):
        if current_subset:
            all_subsets.append(current_subset)
        return all_subsets

    generate_subsets(itemset, index + 1, current_subset + [itemset[index]], all_subsets)

    generate_subsets(itemset, index + 1, current_subset, all_subsets)

    return all_subsets

#function calculates and returns the support for each subset of the itemset
def calculate_subsets_support(itemset, transactions):
    support_res = []
    subsets = generate_subsets(itemset, 0, [], [])
    for subset in subsets:
        if subset == itemset:
            continue
        subset_sup = count_itemset_support(subset, transactions)
        support_res.append((subset, subset_sup))  # Return subset and its support

    return support_res

# calculate the confidence for all subsets of the itemset
def calculate_confidence(itemset, transactions):
    subsets = generate_subsets(itemset, 0, [], [])
    itemset_sup = count_itemset_support(itemset, transactions)

    confidence_res = []
    for subset in subsets:
        if subset == itemset:
            continue
        subset_sup = count_itemset_support(subset, transactions)

        if subset_sup >= minimum_support:  # useless checking cause of (downward closure property)
            conf = itemset_sup / subset_sup
            if conf >= minimum_confidence:
                remaining = [item for item in itemset if item not in subset]
                confidence_res.append((subset, remaining, conf))

    return confidence_res


def calculate_lift(itemset, subset):
    # Calculate support for the full itemset
    itemset_support_count = count_itemset_support(itemset, transactions)
    itemset_support = itemset_support_count / len(transactions)

    # Calculate support for the subset
    subset_support_count = count_itemset_support(subset, transactions)
    subset_support = subset_support_count / len(transactions)

    # Calculate support for the remaining items
    remaining_items = [item for item in itemset if item not in subset]
    remaining_support_count = count_itemset_support(remaining_items, transactions)
    remaining_support = remaining_support_count / len(transactions)

    # Compute the lift if the product of subset and remaining supports is greater than 0
    if subset_support * remaining_support > 0:
        lift = itemset_support / (subset_support * remaining_support)
        return lift
    else:
        return 0


def classify_relationship(lift):
    if lift > 1:
        return "positive relationship :)"
    elif lift < 1:
        return "Negative relationship :)"
    else:
        return "No relation :("


for index, level in enumerate(frequnt_itemset):
    if len(level) == 0:
        continue
    print(f"level {index} frequent itemset:")
    for itemset in level:
        print(itemset)
        confidence_res = calculate_confidence(itemset, transactions)
        sup_res = calculate_subsets_support(itemset, transactions)
        itemset_sup = count_itemset_support(itemset, transactions)
        for subset, remaining, conf in confidence_res:
            print(f"Confidence for {subset} -> {remaining}: {conf}")

root = tk.Tk()
root.title("association rules with lift calculation")

min_support_var = tk.DoubleVar(value=minimum_support)
min_confidence_var = tk.DoubleVar(value=minimum_confidence)

def process_data():
    global minimum_support, minimum_confidence, frequnt_itemset, transactions

    # Get updated support and confidence from the GUI
    minimum_support = min_support_var.get()
    minimum_confidence = min_confidence_var.get()

    # Re-initialize transactions by reading the excel file again
    transactions_excel = pd.read_excel(transactions_excel_file_path)

    # Transform excel input into a transactions hash table <TID, Items>
    transactions = {}
    for _, row in transactions_excel.iterrows():
        key = row['TiD']
        value = row['items'].split(',')
        transactions[key] = value

    # Step 1: Create a one itemsets hash table <Item, Support Count>
    one_itemsets_support_count = defaultdict(int)
    for letter in string.ascii_uppercase:
        for items in transactions.values():
            if letter in items:
                one_itemsets_support_count[letter] += 1

    # Step 2: Prune items with support count less than the minimum support
    for item, support_count in one_itemsets_support_count.items():
        if support_count < minimum_support:
            for items in transactions.values():
                if item in items:
                    items.remove(item)

    # Step 3: Sort the one itemsets descendingly based on the support count
    one_itemsets_support_count = dict(sorted(one_itemsets_support_count.items(), key=lambda x: x[1], reverse=True))

    # Step 4: Create the item ordering based on the support counts
    items_ordering = {char: idx for idx, char in enumerate(one_itemsets_support_count.keys())}

    # Step 5: Sort items in transactions based on the item ordering
    for key, value in transactions.items():
        transactions[key] = sorted(value, key=lambda x: items_ordering.get(x))

    # Step 6: Rebuild the FP-growth tree
    null_node = Node('null', 0)
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

    # Step 7: Reset frequent itemsets and conditional pattern
    current_items = []
    conditional_pattern = {row: {col: 0 for col in one_itemsets_support_count.keys()} for row in one_itemsets_support_count.keys()}

    def dfs(node):
        for item in current_items:
            conditional_pattern[node.name][item] += node.frequency
        if node != null_node:
            current_items.append(node.name)
        for child in node.children:
            dfs(child)
        if node != null_node:
            current_items.pop()

    dfs(null_node)

    # Step 8: Recalculate frequent itemsets
    frequnt_itemset = [[] for _ in range(len(one_itemsets_support_count.keys()))]
    for item in one_itemsets_support_count.keys():
        if one_itemsets_support_count[item] >= minimum_support:
            frequnt_itemset[1].append([item])

    # Step 9: Generate combinations of itemsets
    current_items_to_add = []

    def count(index):
        if index == len(current_items):
            if len(current_items_to_add) > 1:
                frequnt_itemset[len(current_items_to_add)].append(current_items_to_add.copy())
            return
        current_items_to_add.append(current_items[index])
        count(index + 1)
        current_items_to_add.pop()
        count(index + 1)

    for item1 in conditional_pattern.keys():
        for item2 in conditional_pattern[item1].keys():
            if conditional_pattern[item1][item2] >= minimum_support:
                current_items.append(item2)
        current_items_to_add.append(item1)
        count(0)
        current_items_to_add.pop()
        current_items.clear()

    # Step 10: Recalculate and display the results in the output_text widget
    output_text.delete(1.0, tk.END)
    results = []
    for index, level in enumerate(frequnt_itemset):
        if len(level) == 0:
            continue
        results.append(f"Level {index} Frequent Itemsets:")
        for itemset in level:
            results.append(f"Itemset: {itemset}")
            itemset_sup = count_itemset_support(itemset, transactions)
            results.append(f"Support: {itemset_sup}")

            confidence_res = calculate_confidence(itemset, transactions)
            for subset, remaining, conf in confidence_res:
                lift_res = calculate_lift(itemset, subset)
                relationship = classify_relationship(lift_res)
                results.append(f"Confidence for {subset} -> {remaining}: {conf:.2f}")
                results.append(f"Lift: {lift_res:.2f}, Relationship: {relationship}")

    output_text.insert(tk.END, "\n".join(results))



class TreeRepresentation:
    def __init__(self, gui, tree_root):
        self.root = gui
        self.tree_root = tree_root
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.horizontal_spacing = 100
        self.vertical_spacing = 100
        self.draw_tree(self.tree_root, 500, 50)

    def draw_tree(self, node, x, y):
        radius = 20
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="lightblue")
        self.canvas.create_text(x, y, text=f"{node.name}\n{node.frequency}")
        num_children = len(node.children)
        if num_children > 0:
            start_x = x - ((num_children - 1) * self.horizontal_spacing) // 2
            for i, child in enumerate(node.children):
                child_x = start_x + i * self.horizontal_spacing
                child_y = y + self.vertical_spacing
                self.canvas.create_line(x, y + radius, child_x, child_y - radius, fill="black")
                self.draw_tree(child, child_x, child_y)


min_support_label = ttk.Label(root, text="Minimum Support:")
min_support_label.grid(row=0, column=0, padx=10, pady=5)
min_support_entry = ttk.Entry(root, textvariable=min_support_var)
min_support_entry.grid(row=0, column=1, padx=10, pady=5)

min_confidence_label = ttk.Label(root, text="Minimum Confidence:")
min_confidence_label.grid(row=1, column=0, padx=10, pady=5)
min_confidence_entry = ttk.Entry(root, textvariable=min_confidence_var)
min_confidence_entry.grid(row=1, column=1, padx=10, pady=5)

process_button = ttk.Button(root, text="Process Data", command=process_data)
process_button.grid(row=2, column=0, columnspan=2, pady=10)

output_text = tk.Text(root, height=15, width=80)
output_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
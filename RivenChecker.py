import subprocess
import json
import tkinter as tk
from fuzzywuzzy import fuzz
from PIL import Image, ImageTk
import os

# window 
root = tk.Tk()
root.title("Rivenchecker")
root.geometry('500x400')

#defining them as none bc chatgpt suggested it 
output_text = None  
scrollbar = None
#function to check if there is alrdy a textbox/scrollbar displayed and if this is it DESTORYS THEM and returns them to None
def hide():
    global output_text, scrollbar
    if output_text:
        output_text.destroy()
        output_text = None
    if scrollbar:
        scrollbar.destroy()
        scrollbar = None
#function that calculates how similar one name is to another 
def calculate_similarity(name1, name2):
    return fuzz.partial_ratio(name1.lower(), name2.lower())
#this functions only purpose is to let me build this with the warframe.png picture included 
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
#generates curl command to get the JSON content from the endpoint api 
def generate_curl_command(weapon, limit, exact_name=None):
    if exact_name:
        base_url = f"https://api.warframe.market/v1/auctions?type=riven&item_name={exact_name}&limit={limit}"
    else:
        base_url = f"https://api.warframe.market/v1/auctions/search?type=riven&weapon_url_name={weapon}&sort_by=price_desc&limit={limit}"

    curl_command = [
        'curl',
        '-X', 'GET',
        base_url,
        '-H', 'accept: application/json',
        '-H', 'Platform: pc'
    ]

    return curl_command
#this is for displaying the results but does quite a bit more then just that
def display_results(weapon, limit, exact_name=None):
    global output_text, scrollbar  # Use the global variable

    hide()

    # Generate the curl command
    curl_command = generate_curl_command(weapon, limit, exact_name)

    # Execute the curl command and capture the output
    result = subprocess.run(curl_command, capture_output=True, text=True)

    # grab the JSON response
    response_data = json.loads(result.stdout)

    # Extract the top specified number of rivens
    top_rivens = response_data.get('payload', {}).get('auctions', [])

    if not top_rivens and exact_name:
        # If there are no results for the exact name, try to find similar names
        base_url = f"https://api.warframe.market/v1/items?type=riven&name={exact_name}"
        search_command = [
            'curl',
            '-X', 'GET',
            base_url,
            '-H', 'accept: application/json',
            '-H', 'Platform: pc'
        ]
        search_result = subprocess.run(search_command, capture_output=True, text=True)

        # Check if the search response contains valid JSON data
        try:
            search_data = json.loads(search_result.stdout)
        except json.JSONDecodeError:
            return "Error: Unable to retrieve valid data from the API."

        similar_names = search_data.get('payload', {}).get('items', [])

        if similar_names:
            # Sort similar names by fuzzywuzzy partial ratio(dont ask me how this works)
            sorted_similar_names = sorted(similar_names, key=lambda x: calculate_similarity(exact_name, x.get('item_name', '')), reverse=True)
            
            # Display results for the closest match
            return f"No exact match found. Displaying results for '{sorted_similar_names[0]['item_name']}':\n\n" + display_results(weapon, limit, sorted_similar_names[0]['item_name'])
        else:
            return "No results found for the entered Riven name or similar names."

    # Custom sort the rivens by similarity in descending order
    sorted_rivens = sorted(top_rivens, key=lambda x: calculate_similarity(exact_name, x.get('item', {}).get('name', '')), reverse=True)

    if sorted_rivens:
        # Create a scrollbar and attach it to the Text widget
        scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert results into the Text widget
        output_text = tk.Text(root, wrap=tk.WORD, font=("Courier", 10), height=15, width=60, yscrollcommand=scrollbar.set)
        output_text.pack()  # Pack the widget here
        output_text.delete(1.0, tk.END)  # Clear previous content
        scrollbar.config(command=output_text.yview)  # Configure yscrollcommand

        for index, riven in enumerate(sorted_rivens[:limit], start=1):
            item_info = riven.get('item', {})
            item_name = item_info.get('name', 'N/A')
            platinum_price = riven.get('starting_price', 'N/A')
            output_text.insert(tk.END, f"{index}. Name: {item_name}, Price: {platinum_price} platinum\n")
    else:
        output_text = tk.Text(root, wrap=tk.WORD, font=("Courier", 10), height=15, width=60)
        output_text.pack()
        output_text.insert(tk.END, "No results found.")


#GUI STUFF BELOW 

#header 
header_label = tk.Label(root, text="The RivenChecker", font=("Arial", 14, "bold"))
header_label.pack()

#bg
bg_image = Image.open(resource_path("warframe.png"))
bg_image = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1.4)

#this is so they cannot resize the window, disable when bug fixing! 
root.resizable(width=False, height=False)

# Weapon Entry
weapon_label = tk.Label(root, text="Enter a weapon:")
weapon_label.pack()
weapon_entry = tk.Entry(root, width=30)
weapon_entry.pack()

# Exact Name Entry
exact_name_label = tk.Label(root, text="Enter the exact name of the Riven:")
exact_name_label.pack()
exact_name_entry = tk.Entry(root, width=30)
exact_name_entry.pack()

# Limit Entry
limit_label = tk.Label(root, text="Enter the number of results to display:")
limit_label.pack()
limit_entry = tk.Entry(root, width=5)
limit_entry.pack()

# Submit Button
submit_button = tk.Button(root, text="Submit", command=lambda: display_results(weapon_entry.get(), int(limit_entry.get()), exact_name_entry.get()))
submit_button.pack()

# Start the GUI event loop
root.mainloop()

#line to build with pyinstaller
#pyinstaller --icon=favicon.ico --onefile --windowed --add-data "warframe.png;." RivenChecker.py






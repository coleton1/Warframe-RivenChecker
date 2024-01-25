import sys
import PIL
from PIL import ImageTk 
import PIL.Image
import subprocess
import json
import tkinter as tk
from tkinter import *
import customtkinter as ctk
from customtkinter import CTkImage
from customtkinter import *
from fuzzywuzzy import fuzz
import os
import requests

#appearance mode dark,light or system
ctk.set_appearance_mode("system")

# window 
root = ctk.CTk()
root.title("Rivenchecker")
root.geometry('500x400')

output_text = None  
scrollbar = None
root2 = None

#new window when you hit news button
def display_warframe_news():
    global root2

    # Create a new window if it doesn't exist
    if root2 is None or not root2.winfo_exists():
        root2 = CTkToplevel(root)
        root2.geometry('500x500')
        root2.title("Warframe News")
        root2.resizable(width=False, height=False)

        # Fetch news from the Warframe API
        news_url = "https://api.warframestat.us/pc/news"
        response = requests.get(news_url)

        if response.status_code == 200:
            news_data = response.json()
            
            # Display news in the new window
            for news_item in news_data:
                news_title = news_item.get('message', 'N/A')
                news_label = ctk.CTkLabel(root2, text=news_title, font=("Arial", 12,"bold"))
                news_label.pack(pady=5)
        else:
            news_label = ctk.CTkLabel(root2, text="Error fetching Warframe news", font=("Arial", 12, "bold"))
            news_label.pack(pady=5)
    else:
        root2.focus()
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
        
        # Insert results into the Text widget
        
        output_text = ctk.CTkTextbox(root, wrap=tk.WORD, font=("Courier", 13), height=150, width=600) 
        output_text.pack()  # Pack the widget here
        output_text.delete(1.0, ctk.END)  # Clear previous content
        
        for index, riven in enumerate(sorted_rivens[:limit], start=1):
            item_info = riven.get('item', {})
            item_name = item_info.get('name', 'N/A')
            platinum_price = riven.get('starting_price', 'N/A')
            output_text.insert(ctk.END, f"{index}. Name: {item_name}, Price: {platinum_price} platinum\n")
    else:
        output_text = ctk.Text(root, wrap=ctk.WORD, font=("Courier", 10), height=15, width=60)
        output_text.pack()
        output_text.insert(ctk.END, "No results found.")

#GUI STUFF BELOW 

#header 
header_label = ctk.CTkLabel(root, text="The RivenChecker", font=("Arial", 14, "bold"))
header_label.pack()

#IMAGE STUFF
bg_image_path = os.path.join(os.path.dirname(__file__), 'warframeblue.png')
bg_image = PIL.Image.open(resource_path(bg_image_path))
bg1_image = CTkImage(light_image=bg_image, size=(400,400))
bg_label = CTkLabel(root, text="", image=bg1_image)
bg_label.place(relwidth=1, relheight=1.9)
bg_label.text = ""

#this is so they cannot resize the window, disable when bug fixing! 
root.resizable(width=False, height=False)

# Weapon CTkEntry
weapon_label = ctk.CTkLabel(root, text="Enter a weapon:")
weapon_label.pack()
weapon_entry = ctk.CTkEntry(root, width=200)
weapon_entry.pack()

# Exact Name CTkEntry
exact_name_label = ctk.CTkLabel(root, text="Enter the exact name of the Riven:")
exact_name_label.pack()
exact_name_entry = ctk.CTkEntry(root, width=200)
exact_name_entry.pack()
#pretty self explanitory 
creator_label = ctk.CTkLabel(root,text="Made by diefoXD")
creator_label.place(relx=0.01,rely=0.95)

# Limit CTkEntry
limit_label = ctk.CTkLabel(root, text="Enter the number of results to display:")
limit_label.pack()
limit_entry = ctk.CTkEntry(root, width=100)
limit_entry.pack()
#button for warframe news
news_button = ctk.CTkButton(root,width=30,height=20,text="Warframe News",command=display_warframe_news)
news_button.place(x=5,y=5)

# Submit CTkButton
submit_button = ctk.CTkButton(root,width=70,height=30,text="Submit", command=lambda: display_results(weapon_entry.get(), int(limit_entry.get()), exact_name_entry.get()))
submit_button.pack(in_=root, anchor=ctk.W, pady=root.winfo_fpixels(4), padx=(215,0))
# Start the GUI event loop
root.mainloop()

#line to build with pyinstaller
#pyinstaller --icon=favicon.ico --onefile --windowed --add-data "warframeblue.png;." RivenChecker.py

#baro api = https://api.warframestat.us/pc/voidTrader/
#next function will be a function that tells you when baro k'tieer is coming and will include a new button
#check out cherrytree/obsidian for toolbox doc
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
import pywmapi as wm

#appearance mode dark,light or system
ctk.set_appearance_mode("system")

# window 
root = ctk.CTk()
root.title("Rivenchecker")
root.geometry('500x600')   #default 500x400

output_text = None  
scrollbar = None
root2 = None
root3 = None
root4 = None

#displays weapons stats (work in progress)
def weapon_stat_search():
    global root4
    crit_labels = []

    def clear_labels():
        for label in crit_labels:
            label.destroy()
        crit_labels.clear()

    def display_weapon_stats():
        clear_labels()
        weapon_stat_url = f"https://api.warframestat.us/weapons/{weaponstat_entry.get()}"
        response = requests.get(weapon_stat_url)

        if response.status_code == 200:
            weapon_stat_data = response.json()
            attacks = weapon_stat_data.get('attacks',[])
            dispo = weapon_stat_data.get('disposition','N/A')
            rivendis_label = ctk.CTkLabel(root4,text=f"Riven Disposition: {dispo}/5",font=("Arial",12,"bold"))
            rivendis_label.pack()

            
            
            #for different attack modes if weapons have multiple 
            if attacks:
                for index, attack in enumerate(attacks, start=1):
                    attack_name = attack.get('name', f"Attack {index}")
                    crit_chance = attack.get('crit_chance', 'N/A')
                    crit_mult = attack.get('crit_mult','N/A')
                    status_chance = attack.get('status_chance','N/A')
                    damage = attack.get('damage','N/A')
                    multi = weapon_stat_data.get('multishot','N/A')
                    multi2 = weapon_stat_data.get('multishot','N/A')
                    crit_chance_label = ctk.CTkLabel(root4, 
                    text=f"---------------\n{attack_name}\n---------------\n Crit Chance: {crit_chance}\n   Crit Muliplier: {crit_mult} \n Status Chance: {status_chance}\n {damage}\nMultishot: {multi} {multi2}",font=("Arial", 12, "bold"))
                    crit_chance_label.pack()
                    crit_labels.append(crit_chance_label)

                    

            else:
                error_label = ctk.CTkLabel(root4, text="Error fetching weapon stats", font=("Arial", 12, "bold"))
                error_label.pack(pady=20)

    if root4 is None or not root4.winfo_exists():
        root4 = CTkToplevel(root)
        root4.geometry('500x500')
        root4.title("Weapon Stat Search")
        root4.resizable(width=False, height=False)

        weaponstat_label = ctk.CTkLabel(root4, text="Enter a weapon:")
        weaponstat_label.pack()

        weaponstat_entry = ctk.CTkEntry(root4, width=200)
        weaponstat_entry.pack()

        weaponstat_button = ctk.CTkButton(root4, width=30, height=20, text="Submit", command=display_weapon_stats)
        weaponstat_button.pack()

    else:
        root4.focus()
#displays baro information on root3
def display_baro():
    global root3
    if root3 is None or not root3.winfo_exists():
        root3 = CTkToplevel(root)
        root3.geometry('500x500')
        root3.title("Baro Date")
        root3.resizable(width=False, height=False)

        baro_url = "https://api.warframestat.us/pc/voidTrader/"
        response = requests.get(baro_url)

        if response.status_code == 200:
            baro_data = response.json()

            arrival_time = baro_data.get('startString','N/A')
            location = baro_data.get('location','N/A')
            end = baro_data.get('endString','N/A')

            bg_image_path = os.path.join(os.path.dirname(__file__), 'blueimage.png')
            bg_image = PIL.Image.open(resource_path(bg_image_path))
            bg1_image = CTkImage(light_image=bg_image, size=(400, 300))
            bg_label = CTkLabel(root3, text="", image=bg1_image)
            bg_label.place(relwidth=1, relheight=1.5)
            bg_label.text = ""


            location_label = ctk.CTkLabel(root3, text=f"Location: {location}", font=("Arial", 16, "bold",))
            location_label.pack(pady=20)
            arrive_label = ctk.CTkLabel(root3,text=f"Baro Ki'Teer Arrival Time: {arrival_time}",font=("Arial",16,"bold"))
            arrive_label.pack(pady=20)
            end_label = ctk.CTkLabel(root3,text=f"Leaving: {end}",font=("Arial",16,"bold"))
            end_label.pack(pady=20)
        else:
            error_label = ctk.CTkLabel(root3,text="Error fetching data",font=("Arial",16,"bold"))
            error_label.pack(pady=5)

    else:
        root3.focus()
#displays warframe news on root2
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
            for news_item in reversed(news_data):
                news_title = news_item.get('message', 'N/A')
                news_label = ctk.CTkLabel(root2, text=news_title, font=("Arial", 13,"bold"))
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
def calculate_similarity(name1, name2, exact_match):
    if exact_match:
        # Use fuzz ratio for exact match
        return fuzz.ratio(name1.lower(), name2.lower())
    else:
        # Use token set ratio for partial match
        return fuzz.token_set_ratio(name1.lower(), name2.lower())
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

    exact_match = check_var.get() == "on"

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
    sorted_rivens = sorted(top_rivens, key=lambda x: calculate_similarity(exact_name, x.get('item', {}).get('name', ''), exact_match), reverse=True)


    if sorted_rivens:
        
        # Insert results into the Text widget
        
        output_text = ctk.CTkTextbox(root, wrap=tk.WORD, font=("Courier", 13), height=340, width=600) #default h=150 w=600
        output_text.pack()  # Pack the widget here
        output_text.delete(1.0, ctk.END)  # Clear previous content
        
        for index, riven in enumerate(sorted_rivens[:limit], start=1):
            is_direct_sell = riven.get('is_direct_sell', False)


            #broken rn ffs 

            item_info = riven.get('item', {})
            item_name = item_info.get('name', 'N/A')
            platinum_price = riven.get('starting_price', 'N/A')
            owner = riven.get('owner', {})
            ingame = owner.get('ingame_name','N/A')
            attributes = item_info.get('attributes',False)
            output_text.insert(ctk.END, f"--------------\n{index}.Name: {item_name}\nUser: {ingame}\nPrice: {platinum_price} Platinum\n--Attributes--\n")

            for attribute in attributes:
            
                
                value = attribute.get('value','N/A')
                url_name = attribute.get('url_name', 'N/A')
                positive = attribute.get('positive',[]) 
                #add this next "is_direct_sell" to only show the direct sale auctions 
            

                indicator = '+' if positive else '-'
                #indicator = '+' if positive == "true" else '-'
                output_text.insert(ctk.END, f"{indicator} {url_name}: {value}\n")
                
    else:
        output_text = ctk.Text(root, wrap=ctk.WORD, font=("Courier", 10), height=15, width=60)
        output_text.pack()
        output_text.insert(ctk.END, "No results found.")

#GUI STUFF BELOW 

#header 
header_label = ctk.CTkLabel(root, text="The RivenChecker", font=("Arial", 14, "bold"))
header_label.pack()

#IMAGE STUFF
bg_image_path = os.path.join(os.path.dirname(__file__), 'blueimage.png')
bg_image = PIL.Image.open(resource_path(bg_image_path))
bg1_image = CTkImage(light_image=bg_image, size=(400,300))
bg_label = CTkLabel(root, text="", image=bg1_image)
bg_label.place(relwidth=1, relheight=1.5)
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
#button for baro
baro_button = ctk.CTkButton(root,width=30,height=20,text="Baro Arrival Date",command=display_baro)
baro_button.place(x=388,y=5)

weaponstat_button = ctk.CTkButton(root,width=30,height=20,text="Search Weapon Stats",command=weapon_stat_search)
weaponstat_button.place(x=5,y=30)

check_var = ctk.StringVar()
check_var.set("on")

checkbox = ctk.CTkCheckBox(master=root, text="Exact match", variable=check_var, onvalue="on", offvalue="off")
checkbox.place(x=60,y=170)


# Submit CTkButton
submit_button = ctk.CTkButton(root,width=70,height=30,text="Submit", command=lambda: display_results(weapon_entry.get(), int(limit_entry.get()), exact_name_entry.get()))
submit_button.pack(in_=root, anchor=ctk.W, pady=root.winfo_fpixels(4), padx=(215,0))
# Start the GUI event loop
root.mainloop()

#line to build with pyinstaller
#pyinstaller --icon=favicon.ico --onefile --noconsole --collect-all customtkinter --windowed --add-data "blueimage.png;." RivenChecker.py

#weapon search api = https://api.warframestat.us/weapons/{query}

#check out cherrytree/obsidian for toolbox doc
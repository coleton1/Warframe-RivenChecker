import requests
import tkinter as tk
from tkinter import Label  
from PIL import Image
from PIL import ImageTk

def fetch_alert_info():
    response = requests.get('https://api.warframestat.us/pc/alerts')
    data = response.json()

    if isinstance(data, list) and data:
        first_alert = data[0]
        mission_type = first_alert.get('mission', {}).get('type', 'N/A')
        node = first_alert.get('mission', {}).get('node', 'N/A')
        reward_items = first_alert.get('mission', {}).get('reward', {}).get('items', [])
        credits = first_alert.get('mission', {}).get('reward', {}).get('credits', 0)
        expiration_time = first_alert.get('expiry', 'N/A')
         
        organized_info = (                       
            f"Made by Coleton Boutilier\n"
            f"Mission Type: {mission_type}\n"
            f"Node: {node}\n"
            f"Reward: {', '.join(reward_items)} (+{credits}cr)\n"
            f"Expiration Time: {expiration_time}"
        )

        result_label.config(text=organized_info)
    else:
        result_label.config(text="No alerts or something is wong")

grineer_info = ("Grineer = Corrosive & Radiation")
corpus_info = ("Corpus = Magnetic & Toxin")
infest_info = ("Infested = Gas & Viral")
corrupt_info = ("Corrupted = Viral, Heat or Slash")

# main window
window = tk.Tk()
window.title("Warframe Alert Information")
window.geometry('400x300')

# backround stuff 
bg_image = Image.open("warframe.png")
bg_image = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(window, image=bg_image)
bg_label.place(relwidth=1, relheight=1)  # Make the label cover the entire window

# button and label 
fetch_button = tk.Button(window, text="Fetch Alert Info", command=fetch_alert_info)
fetch_button.pack(pady=10)

result_label = tk.Label(window, text="", wraplength=400, justify="left")
result_label.pack(pady=10)

grineer_label = tk.Label(window, text=grineer_info)
grineer_label.place(relx=0.5,rely=0.95,anchor='center')

corpus_label = tk.Label(window, text=corpus_info)
corpus_label.place(relx=0.5,rely=0.89,anchor='center')

infest_label = tk.Label(window, text=infest_info)
infest_label.place(relx=0.5,rely=0.83,anchor='center')

corrupt_label = tk.Label(window, text=corrupt_info)
corrupt_label.place(relx=0.5,rely=0.77,anchor='center')



# main looporoni
window.mainloop()

#need 2 fix bug that turns results into ascii characters or chinese im not entirely sure but it tends to fix itself sometimes

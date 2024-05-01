import tkinter as tk
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageTk
import numpy as np
import os
import warnings
def update_stats():
    obj['time'] = int(entry_minutes.get())*60+int(entry_seconds.get())
    page1['timePlayed'] = int(entry_minutes.get())*60+int(entry_seconds.get())
    kills_sum = page1.groupby('teamId')['kills'].sum()

    # Sum of deaths by teamId
    deaths_sum = page1.groupby('teamId')['deaths'].sum()

    assistss_sum = page1.groupby('teamId')['assists'].sum()

    gold_sum = page1.groupby('teamId')['goldEarned'].sum()
    # If you want to combine these sums into a single DataFrame
    sum_by_team = pd.DataFrame({ 'kills': kills_sum, 'deaths': deaths_sum, 'assists': assistss_sum,'gold': gold_sum})
    page1['UdziałWZabójstwach1'] = (page1['kills'] + page1['assists']) / page1['teamId'].map(sum_by_team['kills'])*100
    page1['UdziałWGold'] = page1['goldEarned'] / page1['teamId'].map(sum_by_team['gold'])*100
    page1.insert(loc=5, column='UdziałWZabójstwach', value=page1['UdziałWZabójstwach1'])
    page1.drop(columns=['UdziałWZabójstwach1'])
    page1['MaxKills'] = page1['kills'] == page1['kills'].max()
    page1['MinDeaths'] = page1['deaths'] == page1['deaths'].min()
    page1['MaxAssist'] = page1['assists'] == page1['assists'].max()
    page1['KDA'] = np.where(page1['deaths'] != 0, (page1['kills'] + page1['assists']) / page1['deaths'], (page1['kills'] + page1['assists']))
    #page1['KDA'] = (page1['kills'] + page1['assists'])/page1['deaths']
    page1['MaxKDA'] = page1['KDA'] == page1['KDA'].max()
    page1['MaxKillparp'] = page1['UdziałWZabójstwach'] == page1['UdziałWZabójstwach'].max()
    page1['MaxGold'] = page1['UdziałWGold'] == page1['UdziałWGold'].max()
    page1['gpm'] = page1['goldEarned']/(page1['timePlayed']/60)
    page1['vpm'] = page1['visionScore']/(page1['timePlayed']/60)
    obj['teamgold'] =obj['teamId'].map(sum_by_team['gold'])


def submit_data():
    global page1, obj
    data = {}
    page1 = pd.DataFrame(columns=labels)
    obj = pd.DataFrame(columns=labels2)
    for i, label_text in enumerate(labels):
        data[label_text] = []
        for j in range(10):  # Iteracja przez każde pole dla danej kolumny
            if label_text == "teamId":
                if j < 5:
                    team_id = 100
                else:
                    team_id = 200
                data[label_text].append(team_id)
            else:
                data[label_text].append(entries[j*len(labels) + i].get())
    
    page1 = page1.append(pd.DataFrame(data), ignore_index=True)
    
    
    data = {}
    for i, label_text in enumerate(labels2):
        data[label_text] = []
        for j in range(2):  # Iteracja przez każde pole dla danej kolumny
            if label_text == "teamId":
                if j < 1:
                    team_id = 100
                else:
                    team_id = 200
                data[label_text].append(team_id)
            else:
                data[label_text].append(entries2[j*len(labels2) + i].get())
    
    obj = obj.append(pd.DataFrame(data), ignore_index=True)
    print("DataFrame po dodaniu nowych danych:")
    for column in page1.columns:
        try:
            page1[column] = page1[column].astype(int)
        except ValueError:
            pass

    print(page1.dtypes)
    update_stats()
    print(obj)
    print(page1)
    generate_grafic()


def bluesideitem(row,image,draw,rowheigth,all_champs):
    green = ImageColor.getcolor('#d2ff76', "RGB")
    purple = ImageColor.getcolor('#7b4bf7', "RGB")
    font = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 37)
    font2 = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 50)
    summonerName=row['summonerName']
    championName=all_champs[all_champs['id']==row['championName']]['name'].values[0]
    semi='|'
    kills =str(row['kills'])
    deaths =str(row['deaths'])
    assists =str(row['assists'])
    kda = "{:.1f}".format(row['KDA'])
    kp="{:.1f}%".format(row['UdziałWZabójstwach'])
    dmg="{:.1f}%".format(row['UdziałWGold'])
    minions = str(row['totalMinionsKilled'])
    vs=str(row['visionScore'])
    vsm="{:.1f}".format(row['vpm'])
    gpm="{:.1f}".format(row['gpm'])
    rowy=rowheigth
    rowx=155

    draw.text((rowx+210, rowy+65), summonerName, font=font, fill=green)
    draw.text((rowx+210, rowy+105), championName, font=font, fill=green)
    draw.text((rowx+730 + 22, rowy+65), semi, font=font, fill=purple)
    draw.text((rowx+795 + 32, rowy+65), semi, font=font, fill=purple)

    deathwithmean = 895+50# np.mean([rowx+730,rowx+795])
    deathwith, height = draw.textsize(deaths,font=font)
    killhwithmean = np.mean([rowx+665,rowx+730])
    killwith, height = draw.textsize(kills,font=font)

    assisthwithmean = np.mean([rowx+795,rowx+860])
    assistswith, height = draw.textsize(assists,font=font)

    draw.text((killhwithmean + 17 - killwith//2 +5, rowy+65), kills, font=font, fill=green)
    draw.text((deathwithmean - deathwith//2 +5, rowy+65), deaths, font=font, fill=green)
    draw.text((assisthwithmean + 32 - assistswith//2 +10, rowy+65), assists, font=font, fill=green)
    KDA_width, height = draw.textsize(kda,font=font2)
    draw.text((deathwithmean - KDA_width//2 +5, rowy+105), kda, font=font2, fill=green)
    icon = Image.open(f'./LoL_Icons/LoLSmall/{row["championName"]}.png')
    size = (160,160)
    position = (rowx+20,rowy+30)
    icon = icon.resize(size)
    image.paste(icon, position)
    kp_width, height = draw.textsize(kp,font=font)
    draw.text((1210 - kp_width//2 +5, rowy+65), kp, font=font, fill=green)

    dmg_width, height = draw.textsize(dmg,font=font)
    draw.text((1210 - dmg_width//2 +5, rowy+105), dmg, font=font, fill=green)

    vs_width, height = draw.textsize(vs,font=font)
    draw.text((1470 - vs_width//2 +5, rowy+65), vs, font=font, fill=green)

    vsm_width, height = draw.textsize(vsm,font=font)
    draw.text((1470 - vsm_width//2 +5, rowy+105), vsm, font=font, fill=green)

    gpm_width, height = draw.textsize(gpm,font=font)
    draw.text((1750 - gpm_width//2 +5, rowy+105), gpm, font=font, fill=green)

    minions_width, height = draw.textsize(minions,font=font)
    draw.text((1750 - minions_width//2 +5, rowy+65), minions, font=font, fill=green)

def redsideitem(row,image,draw,rowheigth,all_champs):
    width = image.width
    green = ImageColor.getcolor('#d2ff76', "RGB")
    purple = ImageColor.getcolor('#7b4bf7', "RGB")
    font = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 37)
    font2 = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 50)
    summonerName=row['summonerName']
    championName=all_champs[all_champs['id']==row['championName']]['name'].values[0]
    semi='|'
    kills =str(row['kills'])
    deaths =str(row['deaths'])
    assists = str(row['assists'])
    kda = "{:.1f}".format(row['KDA'])
    kp="{:.1f}%".format(row['UdziałWZabójstwach'])
    dmg="{:.1f}%".format(row['UdziałWGold'])
    minions = str(row['totalMinionsKilled'])
    vs=str(row['visionScore'])
    vsm="{:.1f}".format(row['vpm'])
    gpm="{:.1f}".format(row['gpm'])
    rowy=rowheigth
    rowx=155
    
    summonernamewidth, _ = draw.textsize(summonerName,font=font)
    draw.text((width-(rowx+210+summonernamewidth), rowy+65), summonerName, font=font, fill=green)
    tempwidth,_ = draw.textsize(championName,font=font)
    draw.text((width-(rowx+210+tempwidth), rowy+105), championName, font=font, fill=green)

    draw.text((width-(rowx+730 + 2), rowy+65), semi, font=font, fill=purple)
    draw.text((width-(rowx+795 + 12), rowy+65), semi, font=font, fill=purple)

    deathwithmean = 925#np.mean([rowx+730,rowx+795])
    deathwith, height = draw.textsize(deaths,font=font)

    assisthwithmean = np.mean([rowx+665,rowx+730])
    killwith, height = draw.textsize(kills,font=font)

    killhwithmean = np.mean([rowx+795,rowx+860])
    assistswith, height = draw.textsize(assists,font=font)

    draw.text((width-(killhwithmean + 12)-killwith//2, rowy+65), kills, font=font, fill=green)
    draw.text((width-(deathwithmean)+5- deathwith//2, rowy+65), deaths, font=font, fill=green)
    draw.text((width-(assisthwithmean - 3 )+5-assistswith//2, rowy+65), assists, font=font, fill=green)
    KDA_width, height = draw.textsize(kda,font=font2)
    draw.text((width-(deathwithmean - KDA_width//2+KDA_width-5), rowy+105), kda, font=font2, fill=green)
    icon = Image.open(f'./LoL_Icons/LoLSmall/{row["championName"]}.png')
    size = (160,160)
    position = (width-(rowx+20+160),rowy+30)
    icon = icon.resize(size)
    image.paste(icon, position)
    kp_width, height = draw.textsize(kp,font=font)
    draw.text((width-(1210 - kp_width//2+kp_width +10), rowy+65), kp, font=font, fill=green)

    dmg_width, height = draw.textsize(dmg,font=font)
    draw.text((width-(1210 - dmg_width//2 +dmg_width+10), rowy+105), dmg, font=font, fill=green)

    vs_width, height = draw.textsize(vs,font=font)
    draw.text((width-(1470 - vs_width//2 +vs_width+10), rowy+65), vs, font=font, fill=green)

    vsm_width, height = draw.textsize(vsm,font=font)
    draw.text((width-(1470 - vsm_width//2 +vsm_width+10), rowy+105), vsm, font=font, fill=green)
    
    minions_width, height = draw.textsize(minions,font=font)
    draw.text((width-(1750 - minions_width//2 +minions_width+10), rowy+65), minions, font=font, fill=green)
    
    gpm_width, height = draw.textsize(gpm,font=font)
    draw.text((width-(1750 - gpm_width//2 +gpm_width+10), rowy+105), gpm, font=font, fill=green)


def createstats(obj_mathc,image,draw):
    green = ImageColor.getcolor('#d2ff76', "RGB")
    purple = ImageColor.getcolor('#7b4bf7', "RGB")
    font = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 199)
    font2 = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 70)
    #1620, 255 730  2000
    timestamp=obj_mathc['time'][0]
    #time = f'{timestamp//60}:'+ "{2f:2f}".format(timestamp%60)
    minutes = timestamp // 60
    seconds = timestamp % 60

    if(obj_mathc.iloc[0]["win"]=="1"):
        draw.text((40, 10), "WIN", font=font, fill=green)
    else:
        draw.text((40, 10), "LOSE", font=font, fill=green)

    if(obj_mathc.iloc[1]["win"]=="1"):
        time_width, height = draw.textsize("WIN",font=font)
        draw.text((image.width - 40 - time_width, 10), "WIN", font=font, fill=green)
    else:
        time_width, height = draw.textsize("LOSE",font=font)
        draw.text((image.width - 40 - time_width, 10), "LOSE", font=font, fill=green)
    time = f"{minutes:02d}:{seconds:02d}"
    time_width, height = draw.textsize(time,font=font)
    draw.text((2000 - time_width//2, 130-height//2), time, font=font, fill=green)
    #1 740

    bluegold = str(obj_mathc['teamgold'][0])
    redgold = str(obj_mathc['teamgold'][1])

    rowblue = obj_mathc.iloc[0]
    time_width, height = draw.textsize(bluegold,font=font2)
    draw.text((1740 - time_width, 400-height//2), bluegold, font=font2, fill=green)
    
    time_width, height = draw.textsize(redgold,font=font2)
    draw.text((image.width-(1740), 400-height//2), redgold, font=font2, fill=green)


    btower = str(rowblue['tower'])
    time_width, height = draw.textsize(btower,font=font2)
    draw.text((363 + 315 - time_width//2, 435+38-height//2), btower, font=font2, fill=green)

    bhorde = str(rowblue['horde'])
    time_width, height = draw.textsize(bhorde,font=font2)
    draw.text((363 - time_width//2, 435+38-height//2), bhorde, font=font2, fill=green)

    bherald = str(rowblue['riftHerald'])
    time_width, height = draw.textsize(bherald,font=font2)
    draw.text((363 - time_width//2, 540+48-height//2), bherald, font=font2, fill=green)


    binhibitor = str(rowblue['inhibitor'])
    time_width, height = draw.textsize(binhibitor,font=font2)
    draw.text((363 +315 - time_width//2,540+48-height//2), binhibitor, font=font2, fill=green)

    bdragon = str(rowblue['dragon'])
    time_width, height = draw.textsize(bdragon,font=font2)
    draw.text((363 +315 - time_width//2, 665+61-height//2), bdragon, font=font2, fill=green)

    bbaron = str(rowblue['baron'])
    time_width, height = draw.textsize(bbaron,font=font2)
    draw.text((363 - time_width//2, 665+61-height//2), bbaron, font=font2, fill=green)

    rowblue = obj_mathc.iloc[1]

    btower = str(rowblue['tower'])
    time_width, height = draw.textsize(btower,font=font2)
    draw.text((image.width-(363 +315 + 50)- time_width//2, 435+38-height//2), btower, font=font2, fill=green)
    
    bhorde = str(rowblue['horde'])
    time_width, height = draw.textsize(bhorde,font=font2)
    draw.text((image.width-(363 + 50)- time_width//2, 435+38-height//2), bhorde, font=font2, fill=green)

    bherald = str(rowblue['riftHerald'])
    time_width, height = draw.textsize(bherald,font=font2)
    draw.text((image.width-(363 + 50)- time_width//2, 540+48-height//2), bherald, font=font2, fill=green)


    binhibitor = str(rowblue['inhibitor'])
    time_width, height = draw.textsize(binhibitor,font=font2)
    draw.text((image.width-(363 +315 + 50)- time_width//2, 540+48-height//2), binhibitor, font=font2, fill=green)
    #540+48-height//2, 435+38-height//2
    bdragon = str(rowblue['dragon'])
    time_width, height = draw.textsize(bdragon,font=font2)
    draw.text((image.width-(363 +315 + 50)- time_width//2, 665+61-height//2), bdragon, font=font2, fill=green)

    bbaron = str(rowblue['baron'])
    time_width, height = draw.textsize(bbaron,font=font2)
    draw.text((image.width-(363 + 50) - time_width//2, 665+61-height//2), bbaron, font=font2, fill=green)


    teamname1 = blue_team_entry.get()
    teamname2 = red_team_entry.get()
    time_width, height = draw.textsize(teamname1,font=font)
    draw.text((1300 - time_width//2, 130-height//2), teamname1, font=font, fill=purple)
    time_width, height = draw.textsize(teamname2,font=font)
    draw.text((2700 - time_width//2, 130-height//2), teamname2, font=font, fill=purple)


def generate_grafic():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    dfblue = page1[page1['teamId']==100].reset_index()
    dfred = page1[page1['teamId']==200].reset_index()
    all_champs = pd.read_csv('allchampsid.csv')


    file = './LoL_Icons/LolTableSmall2.png'
    #file = './LoL_Icons/LolTable.png'#'stretching1.jpg'#
    image = Image.open(file)
    first_rowx=155
    first_rowy=945

    draw = ImageDraw.Draw(image)
    rowheights=[945,1190,1435,1680,1925]
    createstats(obj,image,draw)
    #i=0
    for i, row in dfblue.iterrows():
        bluesideitem(row,image,draw,rowheights[i],all_champs)
    for i, row in dfred.iterrows():
        redsideitem(row,image,draw,rowheights[i],all_champs)

    zapisz(image,"./",'statystyki.png')
    image = image.resize((600, 337))
    img = ImageTk.PhotoImage(image)
    
    # Osadzenie obrazu w etykiecie
    image_label.img = img  # Przechowanie referencji do obrazu
    image_label.config(image=img)
    return
def zapisz(image, folder_path_save, output):
    image.save(os.path.join(folder_path_save, output))
root = tk.Tk()
root.title("Wprowadzanie danych")

labels = [
    "summonerName",
    "championName",
    "kills",
    "deaths",
    "assists",
    "goldEarned",
    "totalMinionsKilled",
    "visionScore",
    "teamId"

]

labels2 = [ "baron", "dragon", "horde", "inhibitor", "riftHerald", "teamId","tower","win"]

page1  = pd.DataFrame(columns=labels)
obj = pd.DataFrame(columns=labels2)
label = tk.Label(root, text="minuty")
label.grid(row=0, column=0, padx=5, pady=5)
entry_minutes = tk.Entry(root, width=5)  # zmniejszenie rozmiaru pola Entry
entry_minutes.grid(row=0, column=1, padx=5, pady=5)
df = pd.DataFrame(columns=labels)
label = tk.Label(root, text="sekundy")
label.grid(row=0, column=2, padx=5, pady=5)
entry_seconds = tk.Entry(root, width=5)  # zmniejszenie rozmiaru pola Entry
entry_seconds.grid(row=0, column=3, padx=5, pady=5)

entries = []
entries2=[]
for i in range(2):  # 10 graczy
    for j, label_text in enumerate(labels2):
        label = tk.Label(root, text=label_text)
        label.grid(row=i+1, column=2*j, padx=5, pady=5)
        entry = tk.Entry(root, width=5)  # zmniejszenie rozmiaru pola Entry
        entry.grid(row=i+1, column=2*j+1, padx=5, pady=5)
        entries2.append(entry)

for i in range(10):  # 10 graczy
    for j, label_text in enumerate(labels):
        label = tk.Label(root, text=label_text)
        label.grid(row=i+3, column=2*j, padx=5, pady=5)
        entry = tk.Entry(root, width=5)  # zmniejszenie rozmiaru pola Entry
        entry.grid(row=i+3, column=2*j+1, padx=5, pady=5)
        entries.append(entry)
blue_team_entry = tk.Entry(root)
blue_team_entry.grid(row=15, column=1, padx=10, pady=5)

red_team_entry = tk.Entry(root)
red_team_entry.grid(row=15, column=3, padx=10, pady=5)
greeting_label = tk.Label(root, text="Drużyna Niebieska")
greeting_label.grid(row=15,column=0)

greeting_label = tk.Label(root, text="Drużyna Czerwona")
greeting_label.grid(row=15,column=2)
# Przycisk do zatwierdzania danych
submit_button = tk.Button(root, text="Submit", command=submit_data)
submit_button.grid(row=16, columnspan=24, pady=10)

image_label = tk.Label(root)
image_label.grid(row=20, columnspan=2, pady=10)

root.mainloop()

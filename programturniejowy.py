import tkinter as tk
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageTk
import numpy as np
import os
import warnings
from datetime import datetime

def main():
    global api_entry, blue_team_entry, red_team_entry, code_entry, image_label
    # Tworzenie okna głównego
    root = tk.Tk()
    root.title("Prosta aplikacja okienkowa")
    warnings.simplefilter("ignore", category=DeprecationWarning)
    warnings.simplefilter("ignore", category=FutureWarning)
    # Tworzenie etykiety w oknie
    #label = tk.Label(root, text="Witaj w mojej prostej aplikacji okienkowej!")
    #label.pack(pady=20)
    greeting_label = tk.Label(root, text="Klucz API")
    greeting_label.grid(row=0)

    greeting_label = tk.Label(root, text="Id gry lub gracza")
    greeting_label.grid(row=2)

    greeting_label = tk.Label(root, text="Drużyna Niebieska")
    greeting_label.grid(row=4,column=0)

    greeting_label = tk.Label(root, text="Drużyna Czerwona")
    greeting_label.grid(row=4,column=1)

    button = tk.Button(root, text="Wczytaj", command=load_data)
    button.grid(row=10,column=0)#.pack(pady=10)
    code_entry = tk.Entry(root)
    code_entry.grid(row=3, padx=10, pady=5)
    api_entry = tk.Entry(root)
    api_entry.grid(row=1, padx=10, pady=5)

    blue_team_entry = tk.Entry(root)
    blue_team_entry.grid(row=5, column=0, padx=10, pady=5)

    red_team_entry = tk.Entry(root)
    red_team_entry.grid(row=5, column=1, padx=10, pady=5)
    image_label = tk.Label(root)
    image_label.grid(row=6, columnspan=2, pady=10)
    # Uruchomienie pętli głównej aplikacji
    root.mainloop()
def load_data():
    global api_key
    api_key = api_entry.get()
    
    if isGameId(code_entry.get()): 
        matchid = code_entry.get()
    else: 
        matchid = getlastgame(code_entry.get())[0]
    
    api_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={api_key}"
    print(api_url)
    match = requests.get(api_url)
    if match.status_code!=200:
        show_error("Błąd",f"Pobierz mecz {match.status_code}, {matchid}" )
        return
    decode_game(match)
    image = generate_grafic()
    
    return image

def wczytaj(folder_path, file):
    try:
        image = Image.open(os.path.join(folder_path, file))
        return image
    except FileNotFoundError:
        print(f"Brakuje {file}")
        return None
    
def generate_grafic():
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
    createstats(obj_mathc,image,draw)
    #i=0
    for i, row in dfblue.iterrows():
        bluesideitem(row,image,draw,rowheights[i],all_champs)
    for i, row in dfred.iterrows():
        redsideitem(row,image,draw,rowheights[i],all_champs)
    image.save("statystyki.png")
    #zapisz(image,"./",'statystyki.png')
    image = image.resize((400, 225))
    img = ImageTk.PhotoImage(image)
    
    # Osadzenie obrazu w etykiecie
    image_label.img = img  # Przechowanie referencji do obrazu
    image_label.config(image=img)
    image_label.grid(row=6, columnspan=2, pady=10)
    create_groups()
    return


def decode_game(match_data):
    global allmatches_df, allplayers_df, allbans_df, page1, obj_mathc
    allmatches_df = pd.DataFrame()
    allplayers_df = pd.DataFrame()
    allbans_df = pd.DataFrame()

# Iterate over listofmatches

    # Extract main game data
    main_data = {k: v for k, v in match_data.json()['info'].items() if k not in ['participants', 'teams']}
    
    # Convert main_data to DataFrame
    matches_df = pd.DataFrame([main_data])
    
    # Extract participants and teams data
    participants_df = pd.DataFrame(match_data.json()['info']['participants'])
    teams_df = pd.DataFrame(match_data.json()['info']['teams'])
    
    # Add gameId to participants and teams DataFrames
    participants_df['gameId'] = match_data.json()['info']['gameId']
    teams_df['gameId'] = match_data.json()['info']['gameId']
    
    # Concatenate or append DataFrames
    allmatches_df = pd.concat([allmatches_df, matches_df], ignore_index=True)
    allplayers_df = pd.concat([allplayers_df, participants_df], ignore_index=True)
    allbans_df = pd.concat([allbans_df, teams_df], ignore_index=True)
    page1 =allplayers_df[allplayers_df['gameId'] == allmatches_df.iloc[0]['gameId']][['summonerName','championName','kills','deaths','assists','goldEarned','win','teamId','neutralMinionsKilled','largestKillingSpree','largestMultiKill','totalMinionsKilled','visionScore','timePlayed','totalDamageDealtToChampions']]
    kills_sum = page1.groupby('teamId')['kills'].sum()

    # Sum of deaths by teamId
    deaths_sum = page1.groupby('teamId')['deaths'].sum()

    assistss_sum = page1.groupby('teamId')['assists'].sum()

    gold_sum = page1.groupby('teamId')['goldEarned'].sum()
    damage_sum = page1.groupby('teamId')['totalDamageDealtToChampions'].sum()
    # If you want to combine these sums into a single DataFrame
    sum_by_team = pd.DataFrame({ 'kills': kills_sum, 'deaths': deaths_sum, 'assists': assistss_sum,'gold': gold_sum,'dmg':damage_sum})
    page1['UdziałWZabójstwach1'] = (page1['kills'] + page1['assists']) / page1['teamId'].map(sum_by_team['kills'])*100
    page1['UdziałWGold'] = page1['goldEarned'] / page1['teamId'].map(sum_by_team['gold'])*100
    page1['UdziałWdmg'] = page1['totalDamageDealtToChampions'] / page1['teamId'].map(sum_by_team['dmg'])*100
    page1.insert(loc=5, column='UdziałWZabójstwach', value=page1['UdziałWZabójstwach1'])
    page1.drop(columns=['UdziałWZabójstwach1'])
    page1['MaxKills'] = page1['kills'] == page1['kills'].max()
    page1['MinDeaths'] = page1['deaths'] == page1['deaths'].min()
    page1['MaxAssist'] = page1['assists'] == page1['assists'].max()
    page1['KDA'] = np.where(page1['deaths'] != 0, (page1['kills'] + page1['assists']) / page1['deaths'], (page1['kills'] + page1['assists']))
    page1['MaxKDA'] = page1['KDA'] == page1['KDA'].max()
    page1['MaxKillparp'] = page1['UdziałWZabójstwach'] == page1['UdziałWZabójstwach'].max()
    page1['MaxGold'] = page1['UdziałWGold'] == page1['UdziałWGold'].max()
    page1['gpm'] = page1['goldEarned']/(page1['timePlayed']/60)
    page1['vpm'] = page1['visionScore']/(page1['timePlayed']/60)
    obj_mathc = pd.DataFrame()
    for i,row  in allbans_df[allbans_df['gameId'] == allmatches_df.iloc[0]['gameId']].iterrows():
        obj = row[['objectives','teamId']]
        objectives_df = pd.DataFrame(obj['objectives'])
        # Dodanie kolumny 'teamId'
        objectives_df['teamId'] = obj['teamId']
        obj_mathc= pd.concat([obj_mathc, objectives_df], ignore_index=True)
    obj_mathc['teamgold'] =obj_mathc['teamId'].map(sum_by_team['gold'])
    obj_mathc['time']=page1['timePlayed'][0]
    unique_page1 = page1.drop_duplicates(subset=['teamId'])

    # Mapowanie wartości 'win' na podstawie 'teamId'
    obj_mathc['win'] = obj_mathc['teamId'].map(unique_page1.set_index('teamId')['win'])
    obj_mathc.loc[obj_mathc['teamId'] == 100, 'team'] = blue_team_entry.get()
    obj_mathc.loc[obj_mathc['teamId'] == 200, 'team'] = red_team_entry.get()
    obj_mathc.to_csv(f"./LoL_Icons/wins/{blue_team_entry.get()}vs{red_team_entry.get()}.csv")
    page1.to_csv(f"./LoL_Icons/page1/{blue_team_entry.get()}vs{red_team_entry.get()}.csv")
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    allmatches_df.to_csv(f"./LoL_Icons/memory/{blue_team_entry.get()}vs{red_team_entry.get()}_allmatches{current_time}.csv")
    allplayers_df.to_csv(f"./LoL_Icons/memory/{blue_team_entry.get()}vs{red_team_entry.get()}_allplayers{current_time}.csv")
    allbans_df.to_csv(f"./LoL_Icons/memory/{blue_team_entry.get()}vs{red_team_entry.get()}_allbans{current_time}.csv")

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
    dmg="{:.1f}%".format(row['UdziałWdmg'])
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
    dmg="{:.1f}%".format(row['UdziałWdmg'])
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

    if(obj_mathc.iloc[0]["win"]==True):
        draw.text((40, 10), "WIN", font=font, fill=green)
    else:
        draw.text((40, 10), "LOSE", font=font, fill=green)

    if(obj_mathc.iloc[3]["win"]==True):
        time_width, height = draw.textsize("WIN",font=font)
        draw.text((image.width - 40 - time_width, 10), "WIN", font=font, fill=green)
    else:
        time_width, height = draw.textsize("LOSE",font=font)
        draw.text((image.width - 40 - time_width, 10), "LOSE", font=font, fill=green)
    time = f"{minutes:02d}:{seconds:02d}"
    time_width, height = draw.textsize(time,font=font)
    draw.text((2000 - time_width//2, 130-height//2), time, font=font, fill=green)
    #1 740

    bluegold = str(obj_mathc['teamgold'][1])
    redgold = str(obj_mathc['teamgold'][3])

    rowblue = obj_mathc.iloc[1]
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

    rowblue = obj_mathc.iloc[3]

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



def getlastgame(playerid):
    api_url = f"https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{playerid}?api_key={api_key}"
    resp = requests.get(api_url)
    player_info = resp.json()
    print(api_url)
    if resp.status_code!=200:
        show_error("Błąd",f"Pobierz gracza {resp.status_code}" )
        return
    puuid = player_info['puuid']
    api_url2 = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={api_key}"
    
    resp = requests.get(api_url2)
    if resp.status_code!=200:
        show_error("Błąd", f"Pobierz mecz {resp.status_code}")
        return
    match_ids = resp.json()

    return match_ids
def zapisz(image, folder_path_save, output):
    image.save(os.path.join(folder_path_save, output))

def show_error(title, message):
    error_window = tk.Toplevel()
    error_window.title(title)
    error_label = tk.Label(error_window, text=message)
    error_label.pack(padx=20, pady=10)
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
    ok_button.pack(pady=5)
def isGameId(id):
    if "EUN1" in id:
        return True
    else:
        False

def init_df(df_group,grupy):
    for grpups in grupy:
        for team in grpups:
            df_group=df_group.append({"team":team,'wins':0,'losses':0,'place':0},ignore_index=True)
    return df_group
def addpoints(groups_df,team,win):
    if win==True:
        groups_df.loc[groups_df['team'] == team, 'wins']+=1
    else:
        groups_df.loc[groups_df['team'] == team, 'losses']+=1
def create_groups():
    grupaA = ['PIW','H&M','SYN','TMK']
    grupaB = ['ATS',"SER",'NSP','GIT']
    grupaC = ['KBI','KZL','TB','GWB']
    grupaD = ['444','BE','NNW','STW']
    grupy = [grupaA,grupaB,grupaC,grupaD]
    # Ścieżka do folderu z plikami CSV
    folder_path = ".\LoL_Icons\wins"
    df_wins = pd.DataFrame()
    columns=['team','wins','losses','place']
    df_groups = pd.DataFrame(columns=columns)  
    df_groups=init_df(df_groups,grupy)
    
    file_list = os.listdir(folder_path)

    # Iteracja po plikach
    for file_name in file_list:
        # Sprawdzenie, czy plik ma rozszerzenie CSV
        if file_name.endswith(".csv"):
            # Pełna ścieżka do pliku
            file_path = os.path.join(folder_path, file_name)
            
            # Wczytanie pliku CSV do ramki danych
            df = pd.read_csv(file_path)
            teama = df.iloc[0][['team','win']]
            teamb = df.iloc[3][['team','win']]
            row={'Drużyna1': teama['team'], 'Wygrane1': teama['win'], 'Drużyna2': teamb['team'], 'Wygrane2': teamb['win']}
            addpoints(df_groups,teama["team"],teama['win'])
            addpoints(df_groups,teamb["team"],teamb['win'])
            df_wins = df_wins.append(row,ignore_index=True)

    grupaAdf = df_groups[df_groups['team'].isin(grupaA)].sort_values('losses').sort_values('wins', ascending=False)
    grupaBdf = df_groups[df_groups['team'].isin(grupaB)].sort_values('losses').sort_values('wins', ascending=False)

    grupaCdf = df_groups[df_groups['team'].isin(grupaC)].sort_values('losses').sort_values('wins', ascending=False)
    grupaDdf = df_groups[df_groups['team'].isin(grupaD)].sort_values('losses').sort_values('wins', ascending=False)
    chechdraw(grupaAdf,df_wins)
    chechdraw(grupaBdf,df_wins)
    chechdraw(grupaCdf,df_wins)
    chechdraw(grupaDdf,df_wins)
    dfs = [grupaAdf.sort_values('place').sort_values('wins', ascending=False), 
       grupaBdf.sort_values('place').sort_values('wins', ascending=False), 
       grupaCdf.sort_values('place').sort_values('wins', ascending=False), 
       grupaDdf.sort_values('place').sort_values('wins', ascending=False)]
    load_groups(dfs)


def load_groups(dfs):
    # Określenie wymiarów obrazu
    width = 2000
    height = 600

    # Utworzenie przezroczystego obrazu
    transparent_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    transparent_image
    draw = ImageDraw.Draw(transparent_image)
    green = ImageColor.getcolor('#d2ff76', "RGB")
    purple = ImageColor.getcolor('#7b4bf7', "RGB")
    # Współrzędne początku i końca linii
    x_coords = [width // 4, width // 2, width * 3 // 4]

    # Rysowanie pionowych linii
    for x in x_coords:
        draw.line([(x, 0), (x, height)], fill=purple, width=5)
    area_width = width // 4
    areas = [(i * area_width, 0, (i + 1) * area_width, height) for i in range(4)]
    text = "GRUPA"

    font = ImageFont.truetype("./LoL_Icons/Unbounded-Regular.ttf", 70)

    # Wymiary tekstu
    text_width, text_height = draw.textsize(text, font=font)
    letters = ['A','B','C','D']
    # Rysowanie tekstu w środku każdej części
    i=0
    for area in areas:
        textin =  text +f" {letters[i]}"
        text_width, text_height = draw.textsize(textin, font=font)
        area_center_x = (area[0] + area[2]) // 2
        area_center_y = (area[1] + area[3]) // 2
        text_position = (area_center_x - text_width // 2, 50)
        draw.text((text_position[0]-3,text_position[1]+3), textin , fill=green, font=font)
        draw.text(text_position, textin , fill=purple, font=font)
        i+=1
    for i, area in enumerate(areas):
        area_center_x = (area[0] + area[2]) // 2
        area_center_y = (area[1] + area[3]) // 2
        
        # Wybieranie wybranych kolumn
        selected_df = dfs[i][['team','wins','losses']]

        
        # Konwersja ramki danych do formatu tekstowego
        i=0
        for x,row in selected_df.iterrows():
            name,wins,losses = row[['team','wins','losses']]
            text_width, text_height = draw.textsize(name, font=font)
            text_position = (area_center_x-125 - text_width//2, 300 + i*70)
            draw.text((text_position[0]-3,text_position[1]+3), name , fill=purple, font=font)
            draw.text(text_position, name , fill=green, font=font)
            winloss_x= area_center_x+125
            text_position = (winloss_x, 300 + i*70)
            draw.text((text_position[0]-3,text_position[1]+3), "-", fill=purple, font=font)
            draw.text(text_position, "-", fill=green, font=font)
            wins = str(wins)
            text_width, text_height = draw.textsize(wins, font=font)
            text_position = (winloss_x-40 - text_width//2, 300 + i*70)
            draw.text((text_position[0]-3,text_position[1]+3), wins, fill=purple, font=font)
            draw.text(text_position, wins, fill=green, font=font)
            wins = str(losses)
            text_width, text_height = draw.textsize(wins, font=font)
            text_position = (winloss_x+70- text_width//2, 300 + i*70)
            draw.text((text_position[0]-3,text_position[1]+3), wins, fill=purple, font=font)
            draw.text(text_position, wins, fill=green, font=font)
            i+=1
        df_text = selected_df.to_string(index=False)
        
        # Wypisanie zawartości ramki danych
        #draw.text((area_center_x, area_center_y), df_text, fill="white", font=font, anchor="mm")
    transparent_image.save("gpoupimage.png")
    #zapisz(transparent_image,"./",'gpoupimage.png')
    #transparent_image

def chechdraw(grupa,df_win):
    for i in range(0,len(grupa)-1):
        row1=grupa.iloc[i]
        row2=grupa.iloc[i+1]
        if (row1['wins'] == row2['wins']) & (row1['losses'] == row2['losses']):
            wartosc_1 = str(row1['team'])
            wartosc_2 = str(row2['team'])
            wynik = df_win[((df_win['Drużyna1'] == wartosc_1) & (df_win['Drużyna2'] == wartosc_2)) |  ((df_win['Drużyna2'] == wartosc_1) & (df_win['Drużyna1'] == wartosc_2))]

            if wynik.empty:
                row1['place']=i
                row2['place']=i+1
                continue
            wynik = wynik.iloc[0]
            
            if row1['team'] == wynik['Drużyna1']:
                if wynik['Wygrane1']=='True':
                    row1['place']=row1['place']
                    row2['place']=i+1
                else:
                    row1['place']=i+1
                    row2['place']=row2['place']
            else:
                if wynik['Wygrane1']=='True':
                    row1['place']=i+1
                    row2['place']=row2['place']
                else:
                    row1['place']=row1['place']
                    row2['place']=i+1
        else:
            row1['place']=row1['place']
            row2['place']=row1['place']+1

        grupa.iloc[i]=row1
        grupa.iloc[i+1]=row2
if __name__ == "__main__":
    main()

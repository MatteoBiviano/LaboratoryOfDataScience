# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 23:10:49 2021

@author: Matteo Biviano, Alice Graziani
Il file contiene il codice utilizzato per splittare tennis.csv nei file richiesti.

"""
import csv

# ------- Directory dove salvare i nuovi file -----
path = "project_data/"

# ------- Input File import -------
tennis = open("tennis.csv", "r")

# ------ Create input readers -----
tennis_ds = csv.reader(tennis, delimiter = ",")

# ------- Output File import -------
match = open(path+"match.csv", "w", newline='')
tournament = open(path+"tournament.csv", "w", newline='')
date = open(path+"date.csv", "w", newline='')
player = open(path+"player_tmp.csv", "w", newline='')

# ------ Create output readers -----
match_writer = csv.writer(match)
tournament_writer = csv.writer(tournament)
date_writer = csv.writer(date)
player_writer = csv.writer(player)

# ------ Set per controllare i distinti -----
match_set  = set()
tournament_set = set() 
date_set = set()

# ------ Dizionario utilizzato per scrivere salvare i campi del player 
#        (utile per dare precedenza ai campi definiti, rispetto ai nan)
players_dict = {}
# ----- Flag per controllare se stiamo leggendo l'header -----
first=True 
# ----- Nuovo id progressivo univoco del player -----
player_new_id = 0
# ----- Nuovo id progressivo univoco del tournament -----
tournament_new_id = 0

# ------ Dizionari usati per mappare i nuovi id ai dati distinti ----
mapped_tournament = {}
mapped_player = {}

"""
La funzione prepara l'header di ogni file di output
@param row: riga con l'header del file originale
"""
def create_header(row):
    # Match header
    match_header = [row[0], "match_id", row[7], row[14]] + row[21:-2]
    # Player header (aggiungiamo "age", "tourney_date", "tourney_id" per poter effettuare le preparazioni filani il prepare_player.py)
    player_header = ["player_id", "old_player_id", "country_id", "name", "hand", "ht", "age", "tourney_date", "tourney_id"]
    # Tournament header
    tournament_header = [row[0], "old_tourney_id", "date_id"] + row[1:5] + row[-2:]
    # Date header
    date_header = ["date_id", "day", "month", "year", "quarter"]
    # Write header
    match_writer.writerow(match_header)
    player_writer.writerow(player_header)
    tournament_writer.writerow(tournament_header)
    date_writer.writerow(date_header)

"""
La funzione prepara la lista di dati di input del torneo e la scrive nel nuovo file
scartando i duplicati
@param tournament_param: lista con i dati da inserire
@param tournament_new_id: nuovo id progressivo che identifica il torneo
"""
def prepare_write_tournament(tournament_param, tournament_new_id):
    ll = tournament_param[:3]
    # ---- Preparazione "surface" ---- 
    if len(tournament_param[3]) == 0:
        ll.append("Hard")# Per lo stesso livello e draw_size sono sempre Hard le superfici
    else:
        ll.append(tournament_param[3])
    ll = ll + tournament_param[4:]
    tournament_writer.writerow([tournament_new_id]+ll)

"""
La funzione prepara la lista di dati di input del player e la scrive nel nuovo file
scartando i duplicati
@param player_param: lista con i dati da inserire [player_id, country_id, name, hand, ht, age, tourney_date]
@param player_new_id: nuovo id del player
@param tournament_new_id: nuovo id del torneo
"""
def store_players(player_param, player_new_id, tournament_new_id):
    if player_param[0] + "+" + player_param[2] not in players_dict:
        players_dict[player_param[0] + "+" + player_param[2]] = {"id": player_param[0],
                                                                 "new_id": player_new_id,
                                                                 "country_id": player_param[1],
                                                                 "name": player_param[2],
                                                                 "hand": [player_param[3]],
                                                                 "ht": [player_param[4]],
                                                                 "age": [player_param[5]],
                                                                 "tourney_date":[player_param[6]],
                                                                 "tourney_id": str(tournament_new_id)}
    else:
        players_dict[player_param[0] + "+" + player_param[2]]["hand"].append(player_param[3])
        players_dict[player_param[0] + "+" + player_param[2]]["ht"].append(player_param[4])
        players_dict[player_param[0] + "+" + player_param[2]]["age"].append(player_param[5])
        players_dict[player_param[0] + "+" + player_param[2]]["tourney_date"].append(player_param[6])

"""
La funzione prepara la lista di dati di input del match e la scrive nel nuovo file
scartando i duplicati
@param ids: lista degli id
@param match_param: lista con i dati, non id, da inserire
"""
def prepare_write_match(ids, match_param):
    ll = []
    # ---- Preparazione "score" ---- 
    if (len(match_param[0]) == 0) or (match_param[0]== ">") or (match_param[0]== "ï¿½") or (match_param[0]== "&nbsp;"):
        # Gestione casi speciali:
        # 1) vuoto - 2) ï¿½  - 3) > - 4) &nbsp;
        ll.append("NOT")
    elif match_param[0]== "Def.":
        # Sostituzione errore
        ll.append("DEF")
    else:
        ll.append(match_param[0])
    # ---- Preparazione  altri campi
    for i in match_param[1:]:
        if len(i)==0:
            # il campo è vuoto
            ll.append("-1")
        else:
            ll.append(i)
    # Se inseriamo un nuovo id del torneo match_id (match_num + new_id) basterebbe a identificare il match
    # quindi potremmo benissimo vedere se match_param[1] è o non in match_set
    to_check = " ".join(ids + ll)
    if to_check not in match_set:
         match_set.add(to_check)
         match_writer.writerow(ids + ll)

"""
La funzione prepara date (date_id) e scrive i dati nel file date.csv
scartando i duplicati
@param date: data iniziale
"""
def prepare_write_date(date):
    if date not in date_set:
        # I primi 4 caratteri corrispondono all'anno
        year = date[:4]
        # I caratteri 4 e 5 corrispondono al mese
        month = date[4:6]
        # Gli ultimi due caratteri corrispondono al giorno
        day = date[6:]
        # Identifichiamo il trimestre in base al valore del mese:
        # [01, 03] -> Q1, [04, 06] -> Q2, [07, 09] -> Q3, [10, 12] -> Q4,
        if month < "04":
            quarter = "Q1"
        elif month < "07":
            quarter = "Q2"
        elif month < "10":
            quarter = "Q3"
        else:
            quarter = "Q4"
        date_set.add(date)
        date_writer.writerow([date, day, month, year, quarter])
"""
La funzione scrive i dati del player nel file player_tmp.csv, dando precedenza ai dati degli attributi
definiti, rispetto ai casi in cui per lo stesso player l'attributo non è definito
"""
def write_player():
    for pl in players_dict:
        # --------------------- Preparazione hand ------------
        hand = "U" # caso hand vuoto --> Assumiamo sia Undefined 
        # Il 62% sono Undefined
        hands = list(set(players_dict[pl]["hand"]))
        if len(hands) > 1:
            # caso {L, U} o {R, U} ---> U = "Undefined"
            """
            ESEMPI: 
                214020 Amina Anshba {'L', 'U'}
                214741 Anastasia Kulikova {'L', 'U'}
                221012 Qinwen Zheng {'R', 'U'}
                223184 Vanessa Ersoz {'R', 'U'}
            """
            if "L" in hands:
                hand = "L"
            else:
                hand = "R"
        else:
            if len(hands[0])!=0:
                hand = hands[0]
        # --------------------- Preparazione ht --------------
        ht = -1 # caso ht nullo => sono il 95%
        hts = set(players_dict[pl]["ht"])
        for h in hts:
            if len(h)>0:
                # Perchè ci sono casi con valori nan e con valori non nan
                """
                ESEMPIO: 203575 Danka Kovinic {169.0, nan}
                """
                if ht == -1:
                    if len(h)<4:
                        #Caso in cui leggiamo '2.0'--> correggiamo l'errore
                        """
                        UNICO ESEMPIO: 215872 Kamilla Rakhimova {20, nan}
                        """
                        ht = 178 # l'altezza effettiva presente da internet della giocatrice è 178m
                    else: 
                        ht = int(float(h))
                else:
                    # ho già memorizzato un valore di ht e ne ho trovato un altro (ht !=-1)
                    """
                    UNICO ESEMPIO: 105676 David Goffin {163.0, 180.0}  nel 2016/7 ha 163.0, dal 2018 al 2021 è 180.0
                    """
                    ht = int((ht + float(h))/2.0) # Inserisco la media delle altezze
        age = ""
        tourney_date = players_dict[pl]["tourney_date"][0] #in caso di età nulla prendo la prima data di torneo ed id trovati
        for idx in range(len(players_dict[pl]["age"])):
            if players_dict[pl]["age"][idx] != "":
                # prendiamo la prima coppia <age, tourney_date> dove age non è nullo
                """
                ESEMPIO: 222966 Dominika Salkova [16.9609856263, 17.1526351814, 17.037645448299997, nan, ...]
                """
                age = players_dict[pl]["age"][idx]
                tourney_date = players_dict[pl]["tourney_date"][idx]
                break
        #Inseriamo il tourney id
        tourney_id = players_dict[pl]["tourney_id"]
        # per country assumiamo solo la prima che vediamo
        """
        UNICO ESEMPIO: 214741 Anastasia Kulikova {'FIN', 'RUS'}
        """
        player_writer.writerow([players_dict[pl]["new_id"], players_dict[pl]["id"], players_dict[pl]["country_id"], players_dict[pl]["name"],hand, ht, age, tourney_date, tourney_id])
        
# ---------------------------------------------------------------------
#
# ------------------- Preparazione files finali -----------------------
#
# ---------------------------------------------------------------------
#
for row in tennis_ds:
    if first:
        # First create header
        create_header(row)
        first = False
    else:
        
        # Se non ho già letto il torneo 
        # (id+name+level è chiave quindi basta per controllare se è già stato letto)
        if row[0]+row[1]+row[4] not in tournament_set:
            tournament_new_id+=1 #vediamo un nuovo torneo, quindi incrementiamo l'id progressivo
            tournament_set.add(row[0]+row[1]+row[4])

            prepare_write_tournament([row[0], row[5]] + row[1:5] + row[-2:], tournament_new_id)
            
            #AGGIUNTA: Mappiamo il valore
            mapped_tournament[tournament_new_id] = {"id":row[0], "name":row[1], "level":row[4]}
        
        # Caso winner
        if row[7] + "+" + row[9] not in players_dict:
            player_new_id +=1 #vediamo un nuovo winner, quindi incrementiamo l'id progressivo
            
            #AGGIUNTA: Mappiamo il valore
            mapped_player[player_new_id] = {"id":row[7], "name":row[9]}
            
        # Salvo il winner: [player_id, country_id, name, hand,ht, age, tourney_date], player_new_id, tournament_new_id
        store_players([row[7], row[12], row[9], row[10], row[11], row[13], row[5]], player_new_id, tournament_new_id)   
        
        # Caso loser
        if row[14] + "+" + row[16] not in players_dict:
            player_new_id +=1 #vediamo un nuovo loser, quindi incrementiamo l'id progressivo
            
            #AGGIUNTA: Mappiamo il valore
            mapped_player[player_new_id] = {"id":row[14], "name":row[16]}
            
        # Salvo il loser: [player_id, country_id, name, hand,ht, age, tourney_date], player_new_id, tournament_new_id
        store_players([row[14], row[19], row[16], row[17], row[18], row[20], row[5]], player_new_id, tournament_new_id)
        
        # Nuovo match_id
        #match_id = int(row[6])*10000
        #prepare_write_match([str(tournament_new_id), str(match_id)+str(tournament_new_id), str(players_dict[row[7] + "+" + row[9]]["new_id"]),
        #                     str(players_dict[row[14] + "+" + row[16]]["new_id"])], row[21:-2])        
        #AGGIUNTA: Mappiamo il valore
        #mapped_match[str(match_id)+str(tournament_new_id)] = {"id_tourney":tournament_new_id, "id_winner":players_dict[row[7] + "+" + row[9]]["new_id"], "id_loser":players_dict[row[14] + "+" + row[16]]["new_id"], "match_num": row[6]}        
        
        # Scrivo il match (usando i nuovi id come winner_id e loser_id)
        prepare_write_match([str(tournament_new_id), row[6]+str(tournament_new_id), str(players_dict[row[7] + "+" + row[9]]["new_id"]),
                             str(players_dict[row[14] + "+" + row[16]]["new_id"])], row[21:-2])
        # Scrivo la data
        prepare_write_date(row[5])
         
tennis.close()
match.close()
tournament.close()
date.close()
# Scrittura dei players
write_player()
player.close()

# -----------------------------------------------------
# 
#               Scrittura delle tabelle di mapping, per mantenere salvate a parte solo le associazioni
#               tra la nuova chiave e la vecchia (frutto della concatenzione tra attributi)
#
# -----------------------------------------------------
tournament = open("project_data/mapping_table/mapped_tournament.csv", "w", newline='')
tournament_writer = csv.writer(tournament)
tournament_writer.writerow(["tourney_new_id, old_id, name, level"])
for i in mapped_tournament:
    tournament_writer.writerow([i, mapped_tournament[i]["id"], mapped_tournament[i]["name"], mapped_tournament[i]["level"] ])
tournament.close()

player = open("project_data/mapping_table/mapped_player.csv", "w", newline='')
player_writer = csv.writer(player)
player_writer.writerow(["player_id, old_id, name"])
for i in mapped_player:
    player_writer.writerow([i, mapped_player[i]["id"], mapped_player[i]["name"]])
player.close()

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 23:10:49 2021

@author: Matteo Biviano, Alice Graziani

Il file contiene codice creato per comprendere meglio i dati ed effettuare analisi preliminari
"""
import pandas as pd
# ---------------------------------------------------------------------
#
# -------------- Metodi per analizzare i players ---------------------
#
# ---------------------------------------------------------------------

"""
La funzione restituisce un dataframe contenente i dati dei player distinti
@param df : dataframe da cui selezionare i dati dei player
@return players: Un dataframe con i dati dei player distinti
"""
def create_distinct_players(df):
    # Selezione dei dati relativi alle informazioni su winner e loser
    winner_data = df[["winner_id", "winner_name", "winner_hand", "winner_ht", "winner_ioc"]]
    loser_data = df[["loser_id", "loser_name", "loser_hand", "loser_ht", "loser_ioc"]]
    # Rename delle colonne per averle univoche tra i due dataframe
    winner_data.rename(columns={'winner_id': 'player_id', 'winner_name': 'name', 
                                'winner_hand': 'hand', 'winner_ht': 'ht', "winner_ioc": "country"}, inplace=True)
    loser_data.rename(columns={'loser_id': 'player_id', 'loser_name': 'name', 
                                'loser_hand': 'hand', 'loser_ht': 'ht', "loser_ioc": "country"}, inplace=True)
    # Creazione di un unico dataframe    
    frames = [winner_data, loser_data]
    resultdf = pd.concat(frames)
    
    # Selezione solo delle righe distinte
    players = resultdf.drop_duplicates()
    print(f" Number of distinct players {len(players)}")
    players.to_csv("distinct_players.csv")
    return players


"""
La funzione controlla se player_id è chiave per val
@param players : dataframe contenenti i dati dei players
@param val: valore di cui testare se player_id è chiave in {name, country}
"""
def pid_key(players, val):
    is_distinct = True
    players_id = players["player_id"]
    for p_id in players_id:
        # Insieme dei val distinti, per lo stesso player_id
        p_val = set(players[players["player_id"] == p_id][val])
        if len(p_val) > 1:
            # Se per uno stesso player_id abbiamo più di un val diverso allora non è chiave
            is_distinct = False
            # Log per sapere quanti violerebbero il vincolo di chiave
            print(f"{p_id}, {p_val}")
    if not is_distinct:
        print(f"player_id is not key for {val}")
    else:
        print(f"player_id is not key for {val}")

"""
La funzione controlla se <player_id, name> è chiave per val
@param players : dataframe contenenti i dati dei players
@param val: valore di cui testare se <player_id, name> è chiave in {hand, ht, country}
"""
def pid_name_key(players, val):
    is_distinct = True
    players_id = players["player_id"]
    for p_id in players_id:
        # Insieme dei nomi distinti, per lo stesso player_id
        p_names = set(players[players["player_id"] == p_id]["name"])
        for name in p_names:
            # Insieme degli hand distinti per una determinata coppia <player_id, name>
            val_set = set(players[(players["player_id"] == p_id) & (players["name"] == name)][val])
            if len(val_set) > 1:
                # Se per uno stesso <player_id, name> abbiamo più di un val diverso allora non è chiave
                is_distinct = False
                # Log per sapere quanti violerebbero il vincolo di chiave
                print(f"{p_id}, {name}, {val_set}")
    if not is_distinct:
        print(f"<player_id, name> is not key for {val}")
    else:
        print(f"<player_id, name> is key for {val}")

"""
La funzione controlla se <player_id, country> è chiave per val
@param players : dataframe contenenti i dati dei players
@param val: valore di cui testare se <player_id, country> è chiave in {name, hand, ht}
"""
def pid_country_key(players, val):
    is_distinct = True
    players_id = players["player_id"]
    for p_id in players_id:
        # Insieme dei country_id distinti, per lo stesso player_id
        p_country = set(players[players["player_id"] == p_id]["country"])
        for cou in p_country:
            # Insieme degli hand distinti per una determinata coppia <player_id, country>
            val_set = set(players[(players["player_id"] == p_id) & (players["country"] == cou)][val])
            if len(val_set) > 1:
                # Se per uno stesso <player_id, country> abbiamo più di un val diverso allora non è chiave
                is_distinct = False
                # Log per sapere quanti violerebbero il vincolo di chiave
                print(f"{p_id}, {cou}, {val_set}")
    if not is_distinct:
        print(f"<player_id, country> is not key for {val}")
    else:
        print(f"<player_id, country> is key for {val}")

"""
La funzione esegue i test sui players
"""
def test_players():
    tennis = pd.read_csv("tennis.csv")
    players = create_distinct_players(tennis)
    # Controllo che players_id non è chiave per name
    pid_key(players, "name")
    # Controllo che players_id non è chiave per country
    pid_key(players, "country")
    # Controllo che <players_id, name> non è chiave per hand
    pid_name_key(players, "hand")
    # Controllo che <players_id, name> non è chiave per ht
    pid_name_key(players, "ht")
    # Controllo che <players_id, name> non è chiave per country
    pid_name_key(players, "country")
    # Controllo che <players_id, country> non è chiave per name
    pid_country_key(players, "name")
    # Controllo che <players_id, country> non è chiave per hand
    pid_country_key(players, "hand")
    # Controllo che <players_id, country> non è chiave per ht
    pid_country_key(players, "ht")
    
test_players()


# ---------------------------------------------------------------------
#
# -------------- Metodi per analizzare i tornei ------------------------
#
# ---------------------------------------------------------------------

def test_tourney():
    tennis = pd.read_csv("tennis.csv")
    dd = tennis[["tourney_id", "tourney_date", "tourney_name", "surface", "draw_size", "tourney_level", "tourney_spectators", "tourney_revenue"]]
    # 1 - Concateniamo id e name e vediamo per cosa è chiave
    dd["new_id"] = dd["tourney_id"]+dd["tourney_name"]
    new_ids = set(dd["new_id"])
    for i in new_ids:
        spect = set(dd[dd["new_id"] ==i]["tourney_spectators"])
        if len(spect)>1:
            print("non chiave per spectators")
        rev = set(dd[dd["new_id"] ==i]["tourney_revenue"])
        if len(rev)>1:
            print("non chiave per revenue")
        date = set(dd[dd["new_id"] ==i]["tourney_date"])
        if len(date)>1:
            print("non chiave per date")    
        level = set(dd[dd["new_id"] ==i]["tourney_level"])
        if len(level)>1:
            print("non chiave per tourney_level")
        surface = set(dd[dd["new_id"] ==i]["surface"])
        if len(surface)>1:
            print("non chiave per surface")
        draw_size = set(dd[dd["new_id"] ==i]["draw_size"])
        if len(draw_size)>1:
            print("non chiave per draw_size")
    # new_id = id+name è chiave per spectators, revenue, date; ma non lo è per draw_size, tourney_level, surface
    # 2 - Concateniamo id e name e level e vediamo per cosa è chiave
    dd["new_id"] = dd["tourney_id"]+dd["tourney_name"]+ [str(i) for i in dd["tourney_level"]]
    new_ids = set(dd["new_id"])
    for i in new_ids:
        surface = set(dd[dd["new_id"] ==i]["surface"])
        if len(surface)>1:
            print("non chiave per surface")
        draw_size = set(dd[dd["new_id"] ==i]["draw_size"])
        if len(draw_size)>1:
            print("non chiave per draw_size")
    # Il new_id = id+name+level è chiave!
    
test_tourney()


"""
La funzione restituisce la lunghezza massima delle parole presenti in una lista.
Utilizzata per capire a che dimensione impostare i tipi su SQL Managment Studio
@param ll: lista di parole
@return max_l: lunghezza massima
"""
def max_len(ll):
    max_l = 0
    for word in ll:
        if len(word)>max_l:
            max_l = len(word)
    return max_l
tennis = pd.read_csv("tennis.csv")
print(max_len(list(tennis["winner_name"])))
print(max_len(list(tennis["loser_name"])))
print(max_len(list(tennis["surface"])))
# ---------------------------------------------------------------------
#
# -------------- Metodi per analizare i missing values ----------------
#
# ---------------------------------------------------------------------
import missingno as msno
import pandas as pd
tennis = pd.read_csv("tennis.csv")
print('\n N° null values:')
print(tennis.isna().sum())
msno.matrix(tennis)

# ---------------------------------------------------------------------
#
# -------------- Metodo per analizzare i gender dei players -----------
#
# ---------------------------------------------------------------------
def check_gender():
    tennis_dd = pd.read_csv("tennis.csv")
    m = pd.read_csv("male_players.csv")
    f = pd.read_csv("female_players.csv")
    males = []
    for i in m.values:
        males.append(str(i[0]) + " " + str(i[1]))
    females = []
    for i in f.values:
        females.append(str(i[0]) + " " + str(i[1]))
    # Controlliamo se il player è Maschio, Femmina, Entrambi (U) oppure se non è presente (N)
    winners_g = []
    losers_g = []
    for i in tennis_dd.values:
        if i[9] in males:
            if i[9] in females:
                winners_g.append("U")
            else:
                winners_g.append("M")
        else:
            if i[9] in females:
                winners_g.append("F")
            else:
                winners_g.append("N")
        if i[16] in males:
            if i[16] in females:
                losers_g.append("U")
            else:
                losers_g.append("M")
        else:
            if i[16] in females:
                losers_g.append("F")
            else:
                losers_g.append("N")
    # Analisi per torneo
    new__dfdf = pd.DataFrame({"tourney_id": list(tennis_dd["tourney_id"]), "tourney_name": list(tennis_dd["tourney_name"]),
                         "tourney_level": list(tennis_dd["tourney_level"]), "winner_id": list(tennis_dd["winner_id"]),
                          "winner_name": list(tennis_dd["winner_name"]),  "winner_g": winners_g, "loser_id": list(tennis_dd["loser_id"]),
                          "loser_name": list(tennis_dd["loser_name"]), "loser_g": losers_g})
    
    ids = set(new__dfdf["tourney_id"])
    for i in ids:
        names =  set(new__dfdf[new__dfdf["tourney_id"] == i]["tourney_name"])
        for n in names:
            levels = set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n)]["tourney_level"])
            for l in levels:
                w_s = set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n) & (new__dfdf["tourney_level"] == l)]["winner_g"])
                l_s= set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n)& (new__dfdf["tourney_level"] == l)]["loser_g"])
                #print(i,n,l, w_s, l_s)
                if w_s != l_s:
                    print(i,n,l, w_s, l_s)
    # Ci sono casi da "disambiguare:
    # 1) 2019-1607 Banja Luka CH C {'M'} {'N', 'M'} --> Abbiamo N in tornei dove sono presenti o solo M o solo F
    # 2) 2017-W-WITF-CHN-02A-2017 Nanjing $15K 15 {'F'} {'F', 'U'} ---> Abbiamo U in tornei dove sono presenti o solo M o solo F
    # 3) 2016-7004 Shenzhen CH C {'U', 'M'} {'N', 'U', 'M'} ---> Abbiamo N e U in tornei dove sono presenti o solo F o solo M
    ids = set(new__dfdf["tourney_id"])
    for i in ids:
        names =  set(new__dfdf[new__dfdf["tourney_id"] == i]["tourney_name"])
        for n in names:
            levels = set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n)]["tourney_level"])
            for l in levels:
                w_s = set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n) & (new__dfdf["tourney_level"] == l)]["winner_g"])
                l_s= set(new__dfdf[(new__dfdf["tourney_id"] == i) & (new__dfdf["tourney_name"] == n)& (new__dfdf["tourney_level"] == l)]["loser_g"])
                #print(i,n,l, w_s, l_s)
                if w_s == l_s:
                    print(i,n,l, w_s, l_s)
check_gender()


# ---------------------------------------------------------------------
#
# -------- In questa parte vengono sostituiti i missing values --------
# --------  relativi a winner_rank, loser_rank,                --------
# --------  winner_rank_points, loser_rank_points              --------
# --------  con la media dei valori                            --------
# ---------------------------------------------------------------------
tennis_df = pd.read_csv("tennis.csv")
w_rank = tennis_df[["winner_id", "winner_name", "winner_rank"]]
w_rank_points = tennis_df[["winner_id", "winner_name", "winner_rank_points"]]
l_rank = tennis_df[["loser_id", "loser_name", "loser_rank"]]
l_rank_points = tennis_df[["loser_id", "loser_name", "loser_rank_points"]]

def substitute_nan(data, id_column, nan_column):
    # nan columns sarà = {winner_rank,winner_rank_points,loser_rank, loser_rank_points}
    player_ids = set(list(data[id_column])) #id_column sarà winner_id o loser_id
    dt_subs_missing = {}
    for idd in player_ids:
        # Prendiamo la media dei valori di rank per ogni id
        mean_id = data[data[id_column]==idd][nan_column].mean()
        # se la media è nulla vuol dire che non abbiamo altri valori definiti di rank per quel giocatore
        if np.isnan(mean_id): 
            #prendiamo la media dei vincitori (o dei perdenti)
            mean_r = data[nan_column].mean()
            dt_subs_missing[idd] = mean_r
        else:
            dt_subs_missing[idd] = mean_id
    new_vals = []
    for i in tennis_df[[id_column, nan_column]].values:
        if np.isnan(i[1]):
            new_vals.append(dt_subs_missing[i[0]])
        else:
            new_vals.append(i[1])
    
    data[nan_column] = new_vals

substitute_nan(tennis_df, "winner_id", "winner_rank")
substitute_nan(tennis_df, "winner_id", "winner_rank_points")
substitute_nan(tennis_df, "loser_id", "loser_rank")
substitute_nan(tennis_df, "loser_id", "loser_rank_points")
tennis_df.to_csv("tennis.csv", index=False)
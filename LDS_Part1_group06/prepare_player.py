# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 23:10:49 2021

@author: Matteo Biviano, Alice Graziani

Il file contiene i procedimenti utilizzati per poter creare il file finale players.csv

"""
import datetime
import csv
import requests
from bs4 import BeautifulSoup

# ------- Directory dove si trovano i file -----
path = "project_data/"

# ---------------------------------------------------------------------
#
# -------------- Creazione del delta tra due giorni consecutivi -------
#
# ---------------------------------------------------------------------

# Età del giocatore X nel torneo avvenuto nel 20190206
age_06F = 23.1211498973
# Età del giocatore X nel torneo avvenuto nel 20190207
age_07F = 23.1238877481
# Delta (distanza di un giorno) tra 15 e 14 Gennaio
delta = age_07F - age_06F

# ---------------------------------------------------------------------
#
# -------------- Test funzioni per delta ------------------------------
#
# ---------------------------------------------------------------------
"""
Procedura che testa il corretto funzionamento del delta, per il caso specifico
in cui il player ha appena compiuto gli anni
"""
def simple_test_delta():
    age = 24.0
    upper_bound = int(age) + 1
    dist_round = round((upper_bound - age)/delta)
    if dist_round == 365:
        return "Delta works correctly"

    return "Delta is not working properly"

"""
Procedura che testa il corretto funzionamento della funzione per il 
calcolo dell'anno di nascita del player 
"""
def test_birth():
    assert 1992 == get_byear(26.6885694730, 20190115, 23)
    assert 1993 == get_byear(25.0001, 20180101, 23)
    assert 1995 == get_byear(float('nan'), 20181101, 23)
    assert 1982 == get_byear(360, 20180101, 23)
    print("Function working properly")

#print(f" Value of Delta for a day = {delta}")
#print(simple_test_delta())
#test_birth()

# ---------------------------------------------------------------------
#
# ------------------- Preparazione player.csv -------------------------
#
# ---------------------------------------------------------------------


# --------------------------------------------------
#
# Funzioni per sostituire i nan con la media delle età per anno
#
# -------------------------------------------------
"""
La funzione calcola la media delle età dei player per anno
@param file: file da leggere
@return years: dizionario nella forma <anno_torneo> : (somma_age, count_age)
"""
def get_avg_age_by_year(file):
    years = {} # dizionario nella forma <anno_torneo> : (somma_age, count_age)
    player = open(file, "r")
    player_ds = csv.reader(player, delimiter = ",") 
    # Check header
    first=True
    for row in player_ds:
        if first:
            # header = player_id,old_player_id,country_id,name,hand,ht,age,tourney_date,tourney_id
            first = False
        else:
            if len(row[-3]) > 0:
                # 1 - controllo che age non sia nulo
                age = float(row[-3])
                # 2 - Controllo se Age ha 3 cifre ===> non serve più perchè le legge giuste
                """
                f, _  = math.modf(age)
                if f == 0.0:
                    print(age)
                    age = int(age/10)
                """
                y = row[-2][0:4]
                if y not in years:
                    years[y] = [age, 1]
                else:
                    years[y][0] += age
                    years[y][1] += 1
    player.close()
    return years
"""
La funzione legge i files relativi ai maschi e alle femmine e scrive due liste dove
ogni valore è la concatenazione di name e surname nella forma name + " " + surname
@param m_file: path del file dei maschi
@param f_file: path del file delle femmine
@return males, females: set di nomi dei giocatori maschi e femmine
"""
def get_gender_set(m_file, f_file):
    females = set()
    female = open(f_file, "r")
    female_ds = csv.reader(female, delimiter = ",")
    is_header = True
    for row in female_ds:
        if is_header:
            is_header = False
        else:
            females.add(row[0] + " " + row[1])
    female.close()
    
    males = set()
    male = open(m_file, "r")
    male_ds = csv.reader(male, delimiter = ",")
    is_header = True
    for row in male_ds:
        if is_header:
            is_header = False
        else:
            males.add(row[0] + " " + row[1])    
    male.close()
    return males, females
"""
La funzione legge il file dei player per creare due dizionar: 
1) Il dizionario player_dict nel quale memorizzare per ogni giocatore se è maschio (M), femmina (F),
    entrambi (U), nessuno dei due (N) [alcuni nomi dei giocatori infatti non combaciano perfettamente].
2) Il dizionario tourney_dict nel quale memorizzare per ogni identificatore di sesso, il numero di 
    giocatori con quel sesso.
@param males: insieme dei player maschi
@param females: insieme dei player femmine
@param player_path: path dove leggere i dati del player
@return player_dict: dizionario della forma <player_id> -> sex in {M, F, U, N}
        tourney_dict: dizionario della forma <tourney_id> -> {"M": countM, "F": countF,
                                                              "U": countU, "N": countN}
"""
def get_gender_dict(males, females, player_path):
    player_dict = {}
    tourney_dict = {}
    # Input file
    player = open(player_path, "r")
    player_ds = csv.reader(player, delimiter = ",")
    is_header = True
    for row in player_ds:
        if is_header:
            is_header = False
        else:
            if row[-1] not in tourney_dict:
                # Se non ho ancora trovato player per il torneo con tourney_id = row[-1] lo inizializzo
                tourney_dict[row[-1]] = {"U":0, "M":0, "F":0, "N":0}
            
            if row[3] in males:
                if row[3] in females:
                    # Caso 1) Il giocatore è presente in entrambi gli insiemi
                    #         scrivo "U"
                    tourney_dict[row[-1]]["U"] += 1
                    player_dict[row[0]] = "U"
                else:
                    # Caso 2) Il giocatore è solo maschio
                    tourney_dict[row[-1]]["M"] += 1
                    player_dict[row[0]] = "M"
            else:
                if row[3] in females:
                    # Caso 3) Il giocatore è solo femmina
                    tourney_dict[row[-1]]["F"] += 1
                    player_dict[row[0]] = "F"
                else:
                    # Caso 4) Il giocatore non è presente nè tra i maschi nè tra le femmine
                    tourney_dict[row[-1]]["N"] += 1
                    player_dict[row[0]] = "N"
    player.close()
    return player_dict, tourney_dict
"""
Funzione che dato l'age e il tourney_date ci dà l'anno di nascita
@param age: età del giocatore
@param tourney_date: data del torneo a cui ha partecipato il giocatore
@param avg_age: dizionario contenente le medie d'età per anno
@return byear: anno di nascita del giocatore
"""
def get_byear(age, tourney_date, avg_age):
    t_year = str(tourney_date)[0:4]    
    # 1 - Se il valore è nan usiamo la media come età
    if len(age) == 0:
        # 1 - Controllo se Age non è null
        # sottraggo all'anno del torneo la media delle età di quell'anno
        byear = int(t_year) - int(avg_age[t_year][0]/avg_age[t_year][1])
        """ 
        Codice che si sarebbe dovuto usare se in avg_age ci fossero stati
        anni mancanti. In quel caso si sarebbe dovuto usare una media globale avg_g, 
        ottenuta modificando la funzione precedente
        if t_year in avg_age:
            byear = int(t_year) - int(avg_age[t_year][0]/avg_age[t_year][1])
        else:
            print(t_year)
            byear = int(t_year) - avg_g
        """
    else:
        age = float(age)
        upper_bound = int(age) + 1
        days_dist = round((upper_bound - age)/delta)
        date_1 = datetime.datetime.strptime(str(tourney_date), "%Y%M%d")
        end_date = date_1 + datetime.timedelta(days=days_dist)
        if date_1.year != end_date.year:
            #Fa il compleanno nell'anno nuovo o nell'anno vecchio
            byear = int(t_year) - int(age)
        else:
            #Fa il compleanno nello stesso anno del torneo
            byear = int(t_year) - int(age) - 1
    return byear
"""
La funzione sceglie il sesso di ogni giocatore disambiguando i casi:
     - U: giocatore sia maschio che femmina
     - N: sesso del giocatore non trovato
@param player_id: id del giocatore di cui trovare il sesso
@param tourney_id id del torneo in cui gioca quel giocatore
@param player_dict: dizionario della forma <player_id> -> sex in {M, F, U, N}
@param  tourney_dict: dizionario della forma <tourney_id> -> {"M": countM, "F": countF,
                                                              "U": countU, "N": countN}
"""
def get_sex(player_id, tourney_id, player_dict, tourney_dict):
    # Caso 1) Il giocatore ha sesso definito    
    if (player_dict[player_id]=="M") or (player_dict[player_id]=="F"):

        return player_dict[player_id]
    
    # Caso 2) Il giocatore è presente sia come maschio che come femmina (sex = U)
    #     o
    # Caso 3) Il giocatore non ha sesso definito (sex = N)
    if (player_dict[player_id]=="U") or (player_dict[player_id]=="N"): 
        # 1) Controllo se in quel torneo oltre a player "U"/"N" sono presenti player
        #       "M" o "F"
        countM = tourney_dict[tourney_id]["M"]
        countF = tourney_dict[tourney_id]["F"]
        
         # 2.2) Il torneo è misto, metto N
        if (countM> 0) and (countF > 0):
            # I rimanenti sono tutti maschi (ma con incongruenze nei nomi)
            # [Cristian Garin, Christopher O'Connell, Lloyd Harris, Pedro Martinez, Daniel Elahi Galan, J.J. Wolf, Sam Groth]
            """
            Cristian Garin -> Christian	Garin, 
            Christopher O'Connell -> Christopher	Oconnell, 
            Lloyd Harris -> Lloyd George Muirhead Harris,
            Pedro Martinez -> Pedro	Martinez Portero, 
            Daniel Elahi Galan -> Daniel Elahi	Galan Riveros, 
            J.J. Wolf, -> Jeffrey John	Wolf
            Sam Groth -> Samuel Groth
            """
            return "M"
        
        # 2.3) Il torneo contiene solo maschi, assumo sia maschio
        if countM > 0:
            return "M"
        
        # 2.4) Il torneo contiene solo femmine, assumo sia femmina
        if countF > 0:
            return "F"
        # 2.5) Gli altri casi dovuti al fatto di prendere in split_fact.py il primo tourney_id
        #     nel quale il giocatore ha partecipato, sono gestiti manualmente (guardando i valori dal csv)
        #       poichè solo 5
        if tourney_id in [95, 1605, 1965]:
            return "M"
        else: #casi con 739, 3830
            return "F"
"""
La funzione prepara il file player come richiesto scrivendo il file out_f
@param infile: file di input
@param avg: dizionario nella forma <anno_torneo> : (somma_age, count_age)
@param player_dict: dizionario della forma <player_id> -> sex in {M, F, U, N}
@param  tourney_dict: dizionario della forma <tourney_id> -> {"M": countM, "F": countF,
                                                              "U": countU, "N": countN}
@param out_f: file in cui scrivere i dati
"""
def prepare_player(infile, avg, player_dict, tourney_dict, out_f):
    # Input file
    player = open(infile, "r")
    player_ds = csv.reader(player, delimiter = ",")
    # Output file
    player_out = open(out_f, "w", newline='')
    player_out_writer = csv.writer(player_out)
    # Check header
    first=True
    for row in player_ds:
        if first:
            # Scrittura dell'header
            player_out_writer.writerow(["player_id", "old_player_id", "country_id", "name", "sex", "hand", "ht", "byear_of_birth"])
            first = False
        else:
            # Otteniamo il birthyear
            # row[6] è age, row[7] è tourney_date
            birthyear = get_byear(row[6], row[7], avg)
            # Otteniamo sex
            # row[0] è player_id, row[-1] è tourney_id
            sex = get_sex(row[0], row[-1], player_dict, tourney_dict)   # NOTA: Parte resa superflua grazie allo scraping (ma mantentua)
            player_out_writer.writerow(row[0:4] + [sex, row[4], row[5], birthyear])
    player.close()
    player_out.close()

"""
La funzione scarica i dati del player dal sito www.tennisexplorer.com
e li salva nel file project_data/scraped_player.csv, che sarà il file definitivo
da caricare nel DW
"""
def scrapy_player_data():
    # Dizionario delle associazioni per il corretto output del file
    trad_dict = {"man": "M", "woman": "F", "left": "L", "right": "R", "U":"U"}
    # ------- Input File import -------
    real_p = open("project_data/player.csv", "r")
    player_df = csv.reader(real_p, delimiter = ",")
    player_csv = open("project_data/scraped_player.csv", "w", newline='')
    player_writer = csv.writer(player_csv)

    is_header = True
    for row in player_df:
        if is_header:
            # Scrittura dell'header del nuovo file
            player_writer.writerow(["player_id","old_player_id","country_id","name","sex","hand","ht","byear_of_birth"])
            is_header = False
        else:
            # Creo il nome nella forma Nome+Cognome (ES: Taylor+Fritz invece di Taylor Fritz)
            p_name2 = row[3].replace(" ", "+") 
            # Cerchiamo il riferimento al player
            url = f"https://www.tennisexplorer.com/list-players/?search-text-pl={p_name2}&country="
            page = requests.get(url)
    
            # Otteniamo il link alla pagina con i dati del giocatore
            find = False
            for i in page.text.split(">"):
                if "/player" in i:
                    if not find:
                        to_search = i.split("/")[2]
                        find = True
            
            # Facciamo lo scraping dei dati del giocatore
            url2 = f"https://www.tennisexplorer.com/player/{to_search}/"
            page = requests.get(url2)
            
            # Uso di BeautifulSoup per crearmi il dizionario con i dati
            soup = BeautifulSoup(page.text, "html.parser")
            
            scrapy_data = soup.find_all("div",{"class": "date"})
            print(row[3])
            #Creiamo il dizionario dei dati
            d = dict(str(s).replace("<div class=\"date\">", "").replace("</div>", "").split(': ') for s in scrapy_data)
            # Lettura dell'altezza e confronto con l'altezza che si ha (sostituiamo solo se troviamo un'altezza definita diversa)
            if "Height / Weight" in d:
                ht = d["Height / Weight"].split(" / ")[0].replace(" cm", "")
            elif "Height" in d: 
                ht = d["Height"].replace(" cm", "")
            else:
                ht = -1
            if ht != row[6]:
                if ht == -1:
                    ht = row[6]
            # Lettura dell'anno di nascita del player e confronto con l'anno che si ha (sostituiamo solo se troviamo un annp definito diverso)
            if "Age" not in d:
                b_year = 0
            else:
                b_year = d["Age"].split(". ")[2].replace(")", "")
            if b_year != row[7]:
                if b_year==0:
                    b_year = row[7]
            # Lettura del sesso del player (tutti definiti)
            if "Sex" not in d:
                sex = "N"
            else:
                sex = d["Sex"]
            # Lettura della mano di battuta del player e confronto con la mano che si ha (sostituiamo solo se troviamo una mano definita diversa)
            if "Plays" not in d:
                hand = "U"
            else:
                hand = d["Plays"]
            if hand != row[5]:
                hand = row[5]

            player_writer.writerow([row[0], row[1], row[2], row[3], sex, hand, ht, b_year])

    player_csv.close()       
    real_p.close()





# --------------------------------------------------------------------------------------
#
#   Una volta effettuato lo scraping nella funzione scrapy_player_data()
#   questa parte è diventata superflua, è stata comunque lasciata nel codice per completezza
#
# Otteniamo in avg_y, per ogni anno, la somma delle età e il numero di giocatori
# in modo tale da poter calcolare la media delle età per anno
avg_y = get_avg_age_by_year(path+"player_tmp.csv")
# Otteniamo le liste di maschi e femmine per non dover rileggere più volte i file csv
males, females = get_gender_set("male_players.csv", "female_players.csv")
# Dizionari di appoggio per disambiguare i casi di sesso mancante o ambiguo
player_dict, tourney_dict = get_gender_dict(males, females,path+"player_tmp.csv")
#
# 
# --------------------------------------------------------------------------------------

# Preparazione e scrittura del player finale
prepare_player(path+"player_tmp.csv", avg_y, player_dict, tourney_dict, path+"player.csv")

# Scaricamento dei dati del player
scrapy_player_data()

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 23:10:49 2021

@author: Matteo Biviano, Alice Graziani

Il file contiene i procedimenti applicati per creare il file geography.csv
"""
import requests
import csv

# Definizione della directory dove salvare i file
path = "project_data/"
# Dizionario di associazioni acronimo_continente -> nome continente
continent = {"EU": "Europe", "AS": "Asia", "NA": "America", "OC": "Oceania", "SA": "America", "AF": "Africa", "AN": "Antarctica"}

"""
La funzione scarica il testo di una pagina e lo inserisce nel file specificato
@param url: url della pagina da scaricare
@param file_name: nome del file nel quale salvare il testo
"""
def download_page(url, file_name):
    page = requests.get(url)
    #print(page.text)
    text_file = open(file_name, "w")
    text_file.write(page.text)
    text_file.close()

"""
La funzione scarica i dati dalla pagina presente in url e li salva nel dizionario countries
@param url: url della pagina da cui scaricare i dati nel formato <country_id>: <country_name>
@return countries: dizionario delle associazione country_id -> country_name
"""
def create_dict_from_url(url):
    # Dizionario dove salviamo <country_id>: <country_name> dall'url
    countries = {}
    page = requests.get(url)
    ll = str(page.content).split("<tr")[1:] #Escludiamo tutti i dati html della pagina
    for i in ll:
        # Sappiamo che i dati delle country sono contenuti tra <tr> </tr>
        s = i.split('>')
        country_name = s[3].split("<")[0] #La terza colonna riguarda i nomi dei paesi
        if len(country_name) > 0:
            # Escludiamo il parsing dei nomi delle colonne
            if country_name[0] == '\\':
                # siamo nel caso in cui la Å viene codificata come \xc3\x85
                # sostituiamo con A
                country_name = "A" + country_name[8:]                
            country_id = s[12].split("<")[0] #L'ottava colonna riguarda i codici IOC
            countries[country_id] = country_name
    return countries  

"""
La funzione restituisce la lista dei country_id presenti in player
@param file_name: path dei file dei players
@return players_c_codes: lista contenente i country codes presenti in players
"""
def get_p_country(file_name):
    player = open(file_name, "r")
    player_csv = csv.reader(player, delimiter = ",")
    players_c_codes = []
    first=True
    for row in player_csv:
        if first:
            #saltiamo l'header
            first = False
        else:
            # player.csv è nel formato player_id,country_id,name,sex,hand,ht,byear_of_birth,new_id
            # quindi country_id è in posizione 1 (row[1])
            if row[2] not in players_c_codes:
                players_c_codes.append(row[2])
    return players_c_codes

"""
La funzione elabora le sorgenti di input per associare a country_name o country_id i linguaggi.
Nel caso di più lingue parlate viene acquisita la prima
@param file_name: nome del file nel quale è salvato il testo
@param countries: file iniziale countries.csv
@return 
    name_id: dizionario nella forma <country_name> : country_id 
    id_language : dizionario nella forma <country_id> : [country_language, continent_name]
"""
def get_languages(file_name, countries):
    
    name_id = {}
    id_language = {}
    # 1 - Nel file file_name sono presenti i nomi dei paesi e gli ID nel formato ISO3
    with open(file_name) as f:
        line = f.readline()
        while line:
            tokens = line.split("\t")
            if "#" not in tokens[0]: # escludiamo le prime righe contenenti "#" come primo carattere
                # Salviamo solo la lingua più frequente (in prima posizione)
                lan = tokens[15].split(",")[0] # In posizione 15 abbiamo la lista di lingue
                # In posizione 1 c'è l'id ISO, in posizione 8 c'è l'acronimo continente
                id_language[tokens[1]] = [lan, continent[tokens[8]]]
                # In posizione 4 c'è il nome
                name_id[tokens[4]] = tokens[1]
            line = f.readline()
            
    # 2 - Vediamo se nel file iniziale countries.csv ci sono id non presenti nel file file_name.
    #     quelli che non ci sono li ritroviamo poi nell'altra sorgente, oppure come [LIB, SIN, TRI]
    #     sono errori da gestire  (i reali id sarebbero {LYB, SGP, TTO})
    # Apertura csv
    country_df = open(countries, "r")
    countries_csv = csv.reader(country_df, delimiter = ",")    
    first = True
    for row in countries_csv: # countries.csv è nella forma country_code,country_name,continent
        if first:
            # Saltiamo l'header
            first = False
        else:
            if row[0] not in id_language:
                # Correggiamo l'errore di battitura
                name = row[1]
                if name == "Urugay":
                    name = "Uruguay"
                if name in name_id: #Se abbiamo comunque il nome vuol dire che l'id è in un formato diverso
                    old_code = name_id[name] #il codice presente nella sorgente
                    name_id[name] = row[0] #sovrascrivo con il nuovo codice
                    # otteniamo la lingua corrispondente dal dizionario creato dal file json
                    id_language[row[0]] = [id_language[old_code][0], row[2]]
                elif row[0] == "POC": #Philippine Olympic Committee
                    name_id["Philippine Olympic Committee"] = "POC"
                    id_language["POC"] = ["en-AU", "Asia"]
                #Non prevediamo il ramo else perchè lo gestiamo usando l'altra sorgente nella funzione write_geography
    country_df.close()
    return name_id, id_language

"""
La funzione scrive il file finale geography.csv cercando per ogni country_id dei players
i dati corrispondenti ai paesi
@param name_id: dizionario nella forma <country_name> : country_id 
@param id_language: dizionario nella forma <country_id> : [country_language, continent_name]
@param players_c_codes: lista dei country_id (distinti) presenti in player.csv
@param countries: dizionario delle associazione country_id -> country_name
@param output_f: file di output in cui scrivere
"""
def write_geography(name_id, id_language, players_c_codes, countries, output_f):
    final_country = open(output_f, "w", newline='')
    final_country_writer = csv.writer(final_country)
    first=True
    # 1 - Scriviamo in output_f le colonne "country_ioc", "continent", "language" sulla base
    #     dei paesi presenti in players_c_codes
    for c_id in players_c_codes:
        if first:
            #scriviamo l'header del file
            final_country_writer.writerow(["country_ioc", "continent", "language"])
            first = False
        else:
            # Gestione dei casi speciali
            if c_id == "AHO": #il vero id è ANT (Netherlands Antilles)
                final_country_writer.writerow(["AHO", id_language["ANT"][1], id_language["ANT"][0][:2]])
            elif c_id == "MRN": #il vero id è ZAF (South Africa)
                final_country_writer.writerow(["MRN", id_language["ZAF"][1], id_language["ZAF"][0][:2]])
            elif c_id == "ITF": #il vero id è ITA (Italia)
                final_country_writer.writerow(["ITF", id_language["ITA"][1], id_language["ITA"][0][:2]])
            elif c_id == "GUD":  #il vero id è GLP (Guadeloupe)
                final_country_writer.writerow(["GUD", id_language["GLP"][1], id_language["GLP"][0][:2]])
            elif c_id == "UNK":  #il vero id è GBR (United Kingdom)
                final_country_writer.writerow(["UNK", id_language["GBR"][1], id_language["GBR"][0][:2]])
            else:
                # Casi non speciali
                if c_id in id_language:
                    final_country_writer.writerow([c_id, id_language[c_id][1], id_language[c_id][0][:2]])
                else:
                    #print(c_id, countries[c_id])
                    # Dobbiamo cercare il paese in countries (mantenendo gli id presenti in player.csv)
                    exist_id = name_id[countries[c_id]] #cerchiamo l'id conosciuto per quel paese
                    final_country_writer.writerow([c_id, id_language[exist_id][1], id_language[exist_id][0][:2]])
    final_country.close()

# -----------------------------------------------------
#       Otteniamo i dati dalle sorgenti
# -----------------------------------------------------

# 1 - Otteniamo prima i dati dalla pagina http://download.geonames.org/export/dump/countryInfo.txt
#     e salviamo i dati in path+geonames.txt
download_page("http://download.geonames.org/export/dump/countryInfo.txt", path+"geonames.txt")

# 2 - Scarichiamo i dati dalla pagina https://www.worlddata.info/countrycodes.php
#     nel dizionario countries: <country_id> -> <country_name>
countries = create_dict_from_url("https://www.worlddata.info/countrycodes.php")

# 3 - Otteniamo i country_id presenti in playes.csv (perchè ce ne sono 30 in più di countries.csv)
players_c_codes = get_p_country(path+"player.csv")

# -----------------------------------------------------
#       Uniamo i dati delle sorgenti per avere due dizionari:
#           id_language: country_id -> [country_language, continent_name]
#           name_id: country_name -> country_id
# -----------------------------------------------------
name_id, id_language = get_languages(path+"geonames.txt", "countries.csv")

# -----------------------------------------------------
#       Creiamo il file finale geography.csv unendo per ogni country_id presente 
#       nei players (in players_c_codes) i dati ottenuti dalle varie sorgenti
# -----------------------------------------------------
write_geography(name_id, id_language, players_c_codes, countries, path+"geography_2.csv")




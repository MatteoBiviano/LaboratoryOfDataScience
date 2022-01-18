# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 23:10:49 2021

@author: Matteo Biviano, Alice Graziani

Il file contiene i procedimenti per caricare i dati sul server
"""
import csv
import pyodbc 

#Apertura della connessione al database 'Group_6_DB' e creazione del cursore 
server = 'tcp:lds.di.unipi.it'
database = 'Group_6_DB'
username = 'Group_6' 
password = '6RJW3B52'
connectionString = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
cnxn = pyodbc.connect(connectionString)
cursor = cnxn.cursor()

# ---------------------------------------------------
#
# Lettura dei file csv, utilizzando il metodo csv.reader 
#
# ---------------------------------------------------
# 1 - File Date
date = open("project_data/date.csv","r") 
date_lines= csv.reader(date, delimiter = ",")
# 2 - Geography
geography = open("project_data/geography.csv","r") 
geography_lines= csv.reader(geography, delimiter = ",")
# 3 - Player
player = open("project_data/scraped_player.csv","r") 
player_lines= csv.reader(player, delimiter = ",")
# 4 - Tournament
tournament = open("project_data/tournament.csv","r") 
tournament_lines= csv.reader(tournament, delimiter = ",")
# 5 - Match
match = open("project_data/match.csv","r") 
match_lines= csv.reader(match, delimiter = ",")

# Creazione del dizionario contenente i readers di ogni tabella associati al nome della tabella
dt_data = {"Date": date_lines, "Geography": geography_lines, 
           "Player": player_lines, "Tournament": tournament_lines,
           "Match": match_lines}
# Scansione del dizionario e caricamenteo dei dati (commit fatto a caricamento ultimato di ogni tabella)
is_header = True
for table_name in dt_data:
    lines = dt_data[table_name]
    sql = ""
    print(table_name)
    for row in lines:
        if is_header:
            count_param = 0
            # creazione della query leggendo l'header
            parametric_vals = ""
            data_st = ""
            for elem in row:
                data_st += elem + ","
                parametric_vals += "?,"
                count_param+=1
            sql = f"INSERT INTO {username}.{table_name}({data_st[:-1]}) VALUES({parametric_vals[:-1]})"
            print(sql)
            is_header = False
        else:
            # Controlliamo per fare il cast ad intero in base ai casi
            if table_name == "Date":
                rows=cursor.execute(sql,(int(row[0]),int(row[1]),int(row[2]),int(row[3]),row[4]))
            if table_name == "Geography":
                rows=cursor.execute(sql,(row[0],row[1],row[2]))
            if table_name == "Player":
                rows=cursor.execute(sql,(int(row[0]),int(row[1]),row[2],row[3], row[4], row[5], int(row[6]), int(row[7])))
            if table_name == "Tournament":
                rows=cursor.execute(sql,(int(row[0]), row[1], int(row[2]), row[3], row[4], row[5], row[6], int(row[7]), float(row[8])))
            if table_name == "Match":
                rows=cursor.execute(sql,(int(row[0]),int(row[1]),int(row[2]),int(row[3]),row[4], int(row[5]), row[6],
                                         int(float(row[7])), int(float(row[8])), int(float(row[9])), int(float(row[10])), int(float(row[11])), int(float(row[12])),
                                         int(float(row[13])), int(float(row[14])), int(float(row[15])), int(float(row[16])), int(float(row[17])), int(float(row[18])),
                                         int(float(row[19])), int(float(row[20])), int(float(row[21])), int(float(row[22])), int(float(row[23])), int(float(row[24])),
                                         int(float(row[25])), int(float(row[26])), int(float(row[27])), int(float(row[28])), int(float(row[29]))))
            print(row)
    cnxn.commit()
    print(f"Done - Table{table_name}")
    print("------------------------------------------")
    is_header = True # ricominciamo il ciclo
#Chiusura file, cursore e connessione       
date.close()
geography.close()
player.close()
tournament.close()
match.close()
cursor.close()
cnxn.close()

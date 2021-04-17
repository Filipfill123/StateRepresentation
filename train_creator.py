import random
from datetime import datetime as dt
import xlsxwriter

def create_trains():
    from_stations = {"Praha": ("z Prahy, z prahy"), "Brno": ("z Brna", "z brna"), "České Budějovice": ("z Čekých Budějovic", "z čekých budějovic", "z Budějovic", "z budějovic"), "Hradec Králové": ("z Hradce Králové", "z hradce králové", "z Hradce", "z hradce"),
            "Jihlava": ("z Jihlavy", "z jihlavy"), "Karlovy Vary": ("z Karlových Varů", "z karlových varů", "z Varů", "z varů"), "Liberec": ("z Liberce", "z liberce"), "Olomouc": ("z Olomouce", "z olomouce"), "Ostrava": ("z Ostravy", "z ostravy"), "Pardubice": ("z Pardubic", "z pardubic"),
            "Plzeň": ("z Plzně", "z plzně"), "Ústí nad Labem": ("z Ústí nad Labem", "z ústí nad labem", "z ústí", "z Ústí"), "Zlín": ("ze Zlína", "z Zlína", "ze zlína", "z zlína")}
            
    to_stations = {"Praha": ("do Prahy, do prahy"), "Brno": ("do Brna", "do brna"), "České Budějovice": ("do Čekých Budějovic", "do čekých budějovic", "do Budějovic", "do budějovic"), "Hradec Králové": ("do Hradce Králové", "do hradce králové", "do Hradce", "do hradce"),
            "Jihlava": ("do Jihlavy", "do jihlavy"), "Karlovy Vary": ("do Karlových Varů", "do karlových varů", "do Varů", "do varů"), "Liberec": ("do Liberce", "do liberce"), "Olomouc": ("do Olomouce", "do olomouce"), "Ostrava": ("do Ostravy", "do ostravy"), "Pardubice": ("do Pardubic", "do pardubic"),
            "Plzeň": ("do Plzně", "do plzně"), "Ústí nad Labem": ("do Ústí nad Labem", "do ústí nad labem", "do ústí", "do Ústí"), "Zlín": ("do Zlína", "do Zlína", "do zlína", "do zlína")}
            
    train_types = {"O": ("osobák", "osobákem", "osobní vlak", "osobním vlakem"), "R": ("rychlík", "rychlíkem"), "ANY": ("jakýmkoliv vlakem")}

    whole_list = list()
    for from_station, value in from_stations.items():
        for to_station, value in to_stations.items():
            if from_station == to_station:
                continue
            i = 0
            while i <= 10:
                starting_time = "00:00:00"
                train_type = random.choice(list(train_types.keys()))
                time_ranges = [10,12,14,15,16,17, 18,19, 20, 21, 23]
                hours, minutes, *seconds = starting_time.split(":")
                hours = int(hours)
                hours = hours + time_ranges[i]
                hours = str(hours)
                new_time = f"{hours}:00:00"
                list_to_append = [from_station, to_station, new_time, train_type]
                whole_list.append(list_to_append)
                i += 1
    return whole_list

def find_train(from_station_in, to_station_in, time_in, train_type_in, whole_list):
    found_trains = list()
    for from_station, to_station, time, train_type in whole_list:
        hours_in, minutes_in, *seconds_in = time_in.split(":")
        hours, minutes, *seconds = time.split(":")
        if train_type_in == "ANY":
            train_type_in = ("O", "R") 
        if (from_station_in == from_station) and (to_station_in == to_station) and (int(hours) > int(hours_in)) and (train_type in train_type_in):
            found_trains.append(hours)
        
    return found_trains


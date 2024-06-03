import numpy as np
import pandas as pd
import requests
import time

def generate_data_frame_of_app_IDs_and_names():
    URL = "http://api.steampowered.com/ISteamApps/GetAppList/v0002"
    response = requests.get(URL)
    list_of_dictionaries_of_app_IDs_and_names = response.json()["applist"]["apps"]
    data_frame_of_app_IDs_and_names = pd.DataFrame(list_of_dictionaries_of_app_IDs_and_names).rename(columns = {"appid": "App_ID", "name": "Name"})
    data_frame_of_app_IDs_and_names.to_csv(path_or_buf = "Data_Frame_Of_App_IDs_And_Names.csv", index = False)

# Specifying multiple appids results in a response with body null.
def generate_URL_for_app_details(cursor):
    data_frame_of_app_IDs_and_names = pd.read_csv(filepath_or_buffer = "Data_Frame_Of_App_IDs_And_Names.csv", dtype = str)
    URL = "https://store.steampowered.com/api/appdetails?appids="
    URL += data_frame_of_app_IDs_and_names.at[cursor, "App_ID"]
    for i in range(cursor + 1, cursor + 10):
        app_ID = data_frame_of_app_IDs_and_names.at[i, "App_ID"]
        if len(URL) + len(",") + len(app_ID) <= 2048:
            URL += "," + app_ID
        else:
            break
    print(URL)

def generate_data_frame_of_game_information():
    data_frame_of_app_IDs_and_names = pd.read_csv(filepath_or_buffer = "Data_Frame_Of_App_IDs_And_Names.csv", dtype = str)
    #with open(file = "Date_Frame_Of_Game_Information.csv", mode = 'w', encoding = 'utf-8') as file:
    #    file.write("App_ID,Type,Name,Metacritic_Score,Set_Of_Genres,Number_Of_Positive_Reviews,Number_Of_Reviews,Note\n")
    number_of_app_IDs = data_frame_of_app_IDs_and_names.shape[0]
    for i in range(164_301, number_of_app_IDs):
        progress = f"{i} / {number_of_app_IDs}"
        app_ID = data_frame_of_app_IDs_and_names.at[i, "App_ID"]
        type = ""
        name = ""
        metacritic_score = ""
        string_representation_of_set_of_genres = ""
        note = ""
        # https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI
        URL = f"https://store.steampowered.com/api/appdetails?appids={app_ID}"

        try:
            response = None
            number_of_timeouts = 4
            index_of_timeout = 1
            while response == None:
                try:
                    start_time = time.time()
                    response = requests.get(URL, timeout = 60)
                    elapsed_time = time.time() - start_time
                    remaining_time = max(1.5 - elapsed_time, 0)
                    time.sleep(remaining_time)
                except requests.exceptions.Timeout:
                    print(f"Timeout {index_of_timeout} of {number_of_timeouts} was reached.\n")
                    index_of_timeout += 1
            if response == None:
                raise requests.exceptions.Timeout(f"{number_of_timeouts} requests timed out.")
            try:
                JSON_object = response.json()
                if JSON_object == None:
                    note += "JSON object for app details was None."
                else:     
                    JSON_subobject = JSON_object[app_ID]
                    if "data" in JSON_subobject:
                        dictionary_of_app_information = JSON_subobject["data"]
                        type = dictionary_of_app_information["type"]
                        name = dictionary_of_app_information["name"].replace(",", "|")
                        if "metacritic" in dictionary_of_app_information:
                            metacritic_score = dictionary_of_app_information["metacritic"]["score"] 
                        else:
                            note += "Key \"metacritic\" was not in dictionary of app information."
                        if "genres" in dictionary_of_app_information:
                            set_of_genres = set()
                            for dictionary_of_genre_information in dictionary_of_app_information["genres"]:
                                description = dictionary_of_genre_information["description"]
                                set_of_genres.add(description)
                            string_representation_of_set_of_genres = "|".join(set_of_genres)
                        else:
                            note += "Key \"genres\" was not in dictionary of app information."
                    else:
                        note += f"Key \"data\" was not in JSON object corresponding to app ID in JSON object for app details."
            except requests.exceptions.JSONDecodeError:
                note += "Response body does not contain valid JSON."
        except requests.exceptions.Timeout as e:
            note += str(e)

        number_of_positive_reviews = ""
        number_of_reviews = ""
        URL = f"https://store.steampowered.com/appreviews/{app_ID}?json=1&filter=all&language=all&review_type=all&purchase_type=all&num_per_page=0"

        try:
            response = None
            number_of_timeouts = 4
            index_of_timeout = 1
            while response == None:
                try:
                    start_time = time.time()
                    response = requests.get(URL, timeout = 60)
                    elapsed_time = time.time() - start_time
                    remaining_time = max(1.5 - elapsed_time, 0)
                    time.sleep(remaining_time)
                except requests.exceptions.Timeout:
                    print(f"Timeout {index_of_timeout} of {number_of_timeouts} was reached.\n")
                    index_of_timeout += 1
            if response == None:
                raise requests.exceptions.Timeout(f"{number_of_timeouts} requests timed out.")
            try:
                JSON_object = response.json()
                if JSON_object == None:
                    note += "JSON object for app reviews was None."
                else:
                    query_summary = JSON_object["query_summary"]
                    if "total_positive" in query_summary:
                        number_of_positive_reviews = query_summary["total_positive"]
                    number_of_reviews = query_summary["total_reviews"]
            except requests.exceptions.JSONDecodeError:
                note += "Response body does not contain valid JSON."
        except requests.exceptions.Timeout as e:
            note += str(e)

        game_information = f"{app_ID},{type},{name},{metacritic_score},{string_representation_of_set_of_genres},{number_of_positive_reviews},{number_of_reviews},{note}\n"
        with open(file = "Date_Frame_Of_Game_Information.csv", mode = 'a', encoding = 'utf-8') as file:
            file.write(game_information)
        print(f"{progress}: {game_information}")

def manipulate_data_frame_of_game_information():
    data_frame = pd.read_csv(filepath_or_buffer = "Date_Frame_Of_Game_Information.csv")
    data_frame = data_frame[data_frame["Set_Of_Genres"].apply(lambda set_of_genres: "RPG" in str(set_of_genres))]
    data_frame["Review_Score"] = data_frame["Number_Of_Positive_Reviews"] / data_frame["Number_Of_Reviews"]
    data_frame["Rating"] = data_frame["Review_Score"] - (data_frame["Review_Score"] - 0.5) * pow(2, -np.log10(data_frame["Number_Of_Reviews"] + 1)) # https://steamdb.info/blog/steamdb-rating/
    data_frame = data_frame.sort_values(by = "Rating", ascending = False)
    data_frame.to_csv(path_or_buf = "Data_Frame_Of_RPG_Information.csv", index = False)

if __name__ == "__main__":
    #generate_data_frame_of_app_IDs_and_names()
    #generate_URL_for_app_details(0)
    #generate_data_frame_of_game_information()
    manipulate_data_frame_of_game_information()
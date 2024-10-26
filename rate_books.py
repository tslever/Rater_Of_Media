import requests
import csv
import os
import time

if not os.path.isfile(path = "books.csv"):
    with open(encoding = "utf-8", file = "books.csv", mode = 'w', newline = '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ISBN", "Title", "Average Rating", "Total Number of Reviews"])

base_url = "https://www.googleapis.com/books/v1/volumes"

def generate_number_with_10_digits():
    for i in range(0, 10**10):
        yield f"{i:010d}"

for first_part_of_isbn in ["", "978", "979"]:

    generator_of_numbers_with_10_digits = generate_number_with_10_digits()

    for number_with_10_digits in generator_of_numbers_with_10_digits:

        isbn = f"{first_part_of_isbn}{number_with_10_digits}"

        value = f"isbn:{isbn}"

        dictionary_of_parameters = {
            'q': value
        }

        try:
            response = requests.get(base_url, params = dictionary_of_parameters)
        except Exception as e:
            with open(encoding = "utf-8", file = "books.csv", mode = 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([isbn, "rate_books.py HANDLED AN EXCEPTION", None, None])
            continue

        time.sleep(60 / 100)

        body_of_response = response.json()

        if "items" in body_of_response:
            
            for item in body_of_response["items"]:

                volume_info = item.get("volumeInfo", {})
                title = volume_info.get("title", None).replace(',', '|')
                average_rating = volume_info.get("averageRating", None)
                ratings_count = volume_info.get("ratingsCount", None)

                print(f"{isbn}, {title}, {average_rating}, {ratings_count}")

                with open(encoding = "utf-8", file = "books.csv", mode = 'a', newline = '') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([isbn, title, average_rating, ratings_count])

        else:

            with open(encoding = "utf-8", file = "books.csv", mode = 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([isbn, None, None, None])
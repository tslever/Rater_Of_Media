import argparse
import csv
import os
import requests
import time


def generate_isbn(isbn_with_which_to_start: str):
    if len(isbn_with_which_to_start) == 10:
        for i in range(int(isbn_with_which_to_start), 9_999_999_999 + 1):
            yield f"{i:010d}"
        isbn_with_which_to_start = "0000000000000"
    if len(isbn_with_which_to_start) == 13:
        for i in range(int(isbn_with_which_to_start), 9_799_999_999_999 + 1):
            yield f"{i:013d}"
    else:
        raise Exception("ISBN with which to start is invalid.")


def rate_books(isbn_with_which_to_start: str, path_to_csv_file: str) -> None:

    if not os.path.isfile(path = path_to_csv_file):
        with open(encoding = "utf-8", file = path_to_csv_file, mode = 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ISBN", "Title", "Average Rating", "Total Number of Reviews"])

    base_url = "https://www.googleapis.com/books/v1/volumes"

    generator_of_isbns = generate_isbn(isbn_with_which_to_start = isbn_with_which_to_start)

    for isbn in generator_of_isbns:

        value = f"isbn:{isbn}"

        dictionary_of_parameters = {
            'q': value
        }

        try:
            response = requests.get(base_url, params = dictionary_of_parameters)
        except Exception as e:
            print(f"{isbn}, rate_books.py HANDLED A GET REQUEST EXCEPTION, {None}, {None}")
            with open(encoding = "utf-8", file = path_to_csv_file, mode = 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([isbn, "rate_books.py HANDLED A GET REQUEST EXCEPTION", None, None])
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
                with open(encoding = "utf-8", file = path_to_csv_file, mode = 'a', newline = '') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([isbn, title, average_rating, ratings_count])

        else:

            print(f"{isbn}, {None}, {None}, {None}")
            with open(encoding = "utf-8", file = path_to_csv_file, mode = 'a', newline = '') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([isbn, None, None, None])


def parse_arguments():
    dictionary_of_arguments = {}
    parser = argparse.ArgumentParser(prog = 'Rate Books', description = 'This program rates books.')
    parser.add_argument('isbn_with_which_to_start', help = 'ISBN with which to start')
    parser.add_argument('path_to_csv_file', help = 'path to CSV file')
    args = parser.parse_args()
    isbn_with_which_to_start = args.isbn_with_which_to_start
    path_to_csv_file = args.path_to_csv_file
    print(f'ISBN with which to start: {isbn_with_which_to_start}')
    print(f'path to CSV file: {path_to_csv_file}')
    dictionary_of_arguments['isbn_with_which_to_start'] = isbn_with_which_to_start
    dictionary_of_arguments['path_to_csv_file'] = path_to_csv_file
    return dictionary_of_arguments


if __name__ == '__main__':
    dictionary_of_arguments = parse_arguments()
    rate_books(
        isbn_with_which_to_start = dictionary_of_arguments["isbn_with_which_to_start"],
        path_to_csv_file = dictionary_of_arguments["path_to_csv_file"]
    )
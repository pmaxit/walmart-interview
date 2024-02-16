import os
import hashlib
import csv
import asyncio
import aiohttp
from datetime import date
from flask import Flask, jsonify, send_file, Blueprint, render_template
import argparse

app = Flask(__name__)
api_bp = Blueprint('api', __name__)

# Function to read urls from txt file
def read_lines_from_file(file_path):
    """
    Read urls from a text file and return a list of urls.

    Args:
    - file_path (str): The path to the text file.

    Returns:
    - list: A list containing lines from the text file.
    """
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


# Function to calculate SHA256 hexdigest of a file
def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

# Function to download a file from a URL asynchronously
async def download_file_async(session, url, dest_file_path):
    async with session.get(url) as response:
        content = await response.read()
        with open(dest_file_path, 'wb') as file:
            file.write(content)

# Function to process a text file and return required data
def process_text_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    word_list = content.split()
    unique_words = set(word_list)

    return {
        'File name': os.path.basename(file_path),
        'Sha256 hexdigest': calculate_sha256(file_path),
        'File size': os.path.getsize(file_path),
        'Word count': len(word_list),
        'Number of unique words': len(unique_words),
        'Todays date': date.today().strftime('%Y-%m-%d')
    }

# Function to download and process a file asynchronously
async def download_and_process_async(session, url, dest_file_path):
    await download_file_async(session, url, dest_file_path)
    return process_text_file(dest_file_path)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")


# Route to return results in JSON
@app.route('/json', methods=['GET'])
def get_json_results():
    downloads_path = app.config['DOWNLOADS_PATH']
    file_results = []
    urls = read_lines_from_file("urls.txt")

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [download_and_process_async(session, url, f'{downloads_path}/downloaded_file_{index}.txt') for index, url in enumerate(urls)]
            file_results.extend(await asyncio.gather(*tasks))

    asyncio.run(main())

    return jsonify(file_results)


# Route to return results as a downloadable CSV file
@app.route('/csv', methods=['GET'])
def get_csv_results():
    downloads_path = app.config['DOWNLOADS_PATH']
    csv_file_path = 'interview.csv'.format(downloads_path)
    txt_file_path = '{}/downloaded_file'.format(downloads_path)
    urls = read_lines_from_file("urls.txt")

    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [download_and_process_async(session, url, f'{txt_file_path}_{index}.txt') for index, url in enumerate(urls)]
            results = await asyncio.gather(*tasks)

            with open(csv_file_path, 'a', newline='') as csvfile:
                fieldnames = ['File name', 'Sha256 hexdigest', 'File size', 'Word count', 'Number of unique words', 'Todays date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if csvfile.tell() == 0:
                    writer.writeheader()
                writer.writerows(results)

    asyncio.run(main())
    return send_file(csv_file_path, as_attachment=True)

def run_app(port, downloads_path, templates_folder):
    app.config['DOWNLOADS_PATH'] = downloads_path
    app.config['TEMPLATES'] = templates_folder
    app.run(port=port, debug=True, host="0.0.0.0")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File Statistics API')
    parser.add_argument('--port', type=int, default=5000, help='Port for the Flask app')
    parser.add_argument('--downloads_path', type=str, default='downloads', help='Downloads directory path')
    parser.add_argument('--templates', type=str, default='templates', help='Template Folder')

    args = parser.parse_args()
    #app.register_blueprint(api_bp, url_prefix='')


    run_app(port=args.port, downloads_path=args.downloads_path, templates_folder=args.templates)
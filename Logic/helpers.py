import re
import csv
import json
from os import path as os_path

class Helpers:
    @staticmethod
    def fetch_links_from_text(text: str):
        result = {
            "website": re.findall(r"https?://[^\s]+", text),
            "email": re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text),
            "social_media": re.findall(r"https?://(?:www\.)?(?:facebook|instagram|twitter|linkedin|tiktok|youtube)\.[^\s]+", text)
        }
        return {k: v if v else [] for k, v in result.items()}

    @staticmethod
    def mix_links(_links):
        links = {}
        for arg in _links:
            for k, v in arg.items():
                links[k] = links.get(k, []) + v
        return links

    @staticmethod
    def from_json_to_excel(file_name: str, input_file_path: str="./data/data.json", output_folder: str = "./data/"):
        if not file_name.endswith('.csv'):
            raise ValueError("Output file should be a CSV file")       
        input_file_path = os_path.abspath(input_file_path)
        output_folder = os_path.abspath(output_folder)
        
        with open(input_file_path, 'r') as file:
            data = json.load(file)

        if isinstance(data, dict):
            data = data.get('items', [])
        elif not isinstance(data, list):
            raise ValueError("JSON structure not recognized")

        max_website_links = max_email_links = max_social_media_links = 0
        for item in data:
            links = item.get('links', {})
            max_website_links = max(max_website_links, len(links.get('website', [])))
            max_email_links = max(max_email_links, len(links.get('email', [])))
            max_social_media_links = max(max_social_media_links, len(links.get('social_media', [])))

        csv_file_name = file_name.replace('.json', '.csv')
        csv_file_path = os_path.join(output_folder, csv_file_name)

        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)

            headers = ['Name', 'Youtube URL', 'Description', 'Subscribers Count', 'Views Count']
            headers += [f'Website Link {i+1}' for i in range(max_website_links)]
            headers += [f'Email {i+1}' for i in range(max_email_links)]
            headers += [f'Social Media Link {i+1}' for i in range(max_social_media_links)]
            writer.writerow(headers)

            for item in data:
                row = [
                    item.get('name', ''),
                    item.get('Youtube_URL', ''),
                    item.get('description', '').replace('\n', ' '),
                    item.get('subscribers_count', ''),
                    item.get('views_count', '')
                ]
                row += item.get('links', {}).get('website', []) + [''] * (max_website_links - len(item.get('links', {}).get('website', [])))
                row += item.get('links', {}).get('email', []) + [''] * (max_email_links - len(item.get('links', {}).get('email', [])))
                row += item.get('links', {}).get('social_media', []) + [''] * (max_social_media_links - len(item.get('links', {}).get('social_media', [])))
                writer.writerow(row)

if __name__ == '__main__':
    Helpers.from_json_to_excel('output.csv')
import asyncio
import json
from collections import deque
from random import randint
from innertube import InnerTube
from threading import Thread
import re
import csv
import json
from os import path as os_path
# Anime editing 
# Who is strongest 
# Anime 1v1 
# Anime debates
# Anime character comparison

MAX_TASKS = 10

KEYWORD = "Anime character comparison"
CHANNELS_TO_SCRAPE = 5
MIN_SUBCOUNT = 2000

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
                
class ChannelsScrapper(Thread):
    def __init__(self, api=None):
        super().__init__()  # This calls the __init__ method of the base class Thread
        self.keyword = KEYWORD
        self.filters = {"min_subcount": MIN_SUBCOUNT}
        
        self.limit = CHANNELS_TO_SCRAPE
        self.max_tasks = MAX_TASKS
        self._channels_ids: list = []
        self.channels: list = []
        self._continuation = None
        self.client = InnerTube("WEB")

    @property
    def time_to_wait(self):
        return randint(1000, 5000) / 1000
    
    def configure(self, keyword: str=None, filters: dict=None, limit: int=None, max_tasks: int=None):
        if keyword:
            self.keyword = keyword
        if filters:
            self.filters = filters
        if limit:
            self.limit = limit
        if max_tasks:
            self.max_tasks = max_tasks
    

    def _print_progress_bar(self, iteration, total, prefix='', suffix='', length=50, fill='█'):
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end="\r")
        if iteration == total:
            print()

    async def run_async(self):
        await self._get_channels()
        await self._get_channel_data()
        await self.save_data()
        
    def run(self):
        asyncio.run(self.run_async())
        Helpers.from_json_to_excel("output2.csv")

    async def _get_channels(self):
        while len(self._channels_ids) < self.limit:
            await asyncio.sleep(self.time_to_wait)
            items = []

            if self._continuation is not None:
                data = self.client.search(continuation=self._continuation)
                interesting_data = data["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"]
                items = interesting_data[0]["itemSectionRenderer"]["contents"]
            else:
                data = self.client.search(self.keyword)
                interesting_data = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
                items = interesting_data[0]["itemSectionRenderer"]["contents"]

            tasks = []
            for item in items:
                self._print_progress_bar(len(self._channels_ids), self.limit, prefix='Progress:', suffix='Complete', length=50)
                if "reelShelfRenderer" in item:
                    list_of_videos_ids = [x["reelItemRenderer"]["videoId"] for x in item["reelShelfRenderer"]["items"][0:5]]
                    for video_id in list_of_videos_ids:
                        tasks.append(self._fetch_channel_id_from_video(video_id))
                        print("The number of tasks is: ", len(tasks))
            
                elif "videoRenderer" in item:
                    channel_id = item["videoRenderer"]["ownerText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"]["browseId"]
                    if channel_id not in self._channels_ids:
                        self._channels_ids.append(channel_id)
                else:
                    continue
                if len(self._channels_ids) >= self.limit:
                    break
                
            if tasks:
                await asyncio.gather(*tasks)

            if len(self._channels_ids) >= self.limit or len(items) < 2:
                break

            self._continuation = interesting_data[1]["continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]

        self._continuation = None
        print(f"Found {len(self._channels_ids)} channels")
        return self._channels_ids
        
    async def _fetch_channel_id_from_video(self, video_id: str):
        data = self.client.next(video_id)
        # Logic to parse the data and extract channel ID
        # This is a placeholder; you'll need to adapt it based on the actual structure of the data returned by self.client.browse
        channel_id = data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['title']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']
        if channel_id not in self._channels_ids:
            self._channels_ids.append(channel_id)

    async def _get_channel_data(self):
        deque_channels = deque(self._channels_ids)
        tasks = []

        while deque_channels:
            self._print_progress_bar(len(self._channels_ids) - len(deque_channels), len(self._channels_ids), prefix='Getting contacts:', suffix='Complete', length=50)
            try:
                channel_id = deque_channels.popleft()
                if not channel_id:
                    continue

                tasks.append(asyncio.create_task(self._get_channel_contacts(channel_id)))

                if len(tasks) >= self.max_tasks:
                    await asyncio.gather(*tasks)
                    tasks = []

            except Exception as e:
                print(e)
                deque_channels.append(channel_id)

        await asyncio.gather(*tasks)

    async def _get_channel_contacts(self, channel_id):
        channel_data = self.client.browse(channel_id)

        channel_name = channel_data["metadata"]["channelMetadataRenderer"]["title"]
        channel_description = channel_data["metadata"]["channelMetadataRenderer"]["description"]
        try:
            first_video_description = channel_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelVideoPlayerRenderer']['description']['runs'][0]['text']
        except:
            first_video_description = None

        links_1 = Helpers.fetch_links_from_text(channel_description)
        links_2 = Helpers.fetch_links_from_text(first_video_description) if first_video_description else {"website": [], "email": [], "social_media": []}

        try:
            about_page_continuation_token = channel_data['header']['c4TabbedHeaderRenderer']['tagline'][
                'channelTaglineRenderer'
            ]['moreEndpoint']['showEngagementPanelEndpoint']['engagementPanel']['engagementPanelSectionListRenderer']['content'][
                'sectionListRenderer'
            ]['contents'][0]['itemSectionRenderer']['contents'][0]['continuationItemRenderer']['continuationEndpoint'][
                'continuationCommand'
            ]['token']

            await asyncio.sleep(self.time_to_wait)
            about_page_data = self.client.browse(continuation=about_page_continuation_token)

            important_data = about_page_data['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction']['continuationItems'][0]['aboutChannelRenderer']['metadata']['aboutChannelViewModel']
            subs_count = important_data['subscriberCountText'].split(" ")[0]
            if subs_count[-1] == "K":
                subs_count = int(float(subs_count[:-1]) * 1000)
            elif subs_count[-1] == "M":
                subs_count = int(float(subs_count[:-1]) * 1000000)
            else:
                subs_count = int(subs_count)
            if subs_count < self.filters.get("min_subcount", 0):
                return

            

        except:
            about_page_continuation_token = None
            important_data = None
            
        try:
            buffer = " ".join(["https://www."+x["channelExternalLinkViewModel"]['link']["content"] for x in important_data['links']])
            links_3 = Helpers.fetch_links_from_text(buffer)
        except:
            links_3 = {"website": [], "email": [], "social_media": []}
            
        links = Helpers.mix_links([links_1, links_2, links_3])
        if len(links["website"]) == 0 and len(links["email"]) == 0 and len(links["social_media"]) == 0:
            return
        channel_data = {
            "name": channel_name,
            "Youtube_URL": "https://www.youtube.com/channel/"+channel_id,
            "description": channel_description,
            "subscribers_count": important_data['subscriberCountText'] if important_data else None,
            "views_count": important_data['viewCountText'] if important_data else None,
            "links": links
        }
        

        self.channels.append(channel_data)

    def _filter_channels(self):
        pass

    async def save_data(self):
        with open("./data/data.json", "w") as f:
            json.dump(self.channels, f, indent=4)


class ParamsTypes:
    PARAMS_TYPE_VIDEO: str = "EgIQAQ%3D%3D"
    PARAMS_TYPE_CHANNEL: str = "EgIQAg%3D%3D"
    PARAMS_TYPE_PLAYLIST: str = "EgIQAw%3D%3D"
    PARAMS_TYPE_FILM: str = "EgIQBA%3D%3D"


if __name__ == "__main__":
    scrapper = ChannelsScrapper()
    scrapper.start()
    print("Done")
    scrapper.join()

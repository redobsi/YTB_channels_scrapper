from queue import Queue
from Logic.ytb_channels_scrapper import ChannelsScrapper
from Interface.front import Contacts_Generator_UI_wrapper

class API:
    def __init__(self):
        self.queue_to_backend = Queue()
        self.queue_to_frontend = Queue()
        self.global_data = dict()
        
    def pull_data(self):
        return self.queue_to_frontend.get()
    
    def push_data(self, data):
        self.queue_to_frontend.put(data)
        
    def get_data(self, key):
        return self.global_data.get(key, [])
    
    def set_data(self, key, value):
        self.global_data[key] = value


class Mediator:
    def __init__(self):
        self.api = API()

    def start_communication(self):
        self.frontend = Contacts_Generator_UI_wrapper(api=self.api)
        self.backend = ChannelsScrapper(api=self.api)

        self.frontend.run()
        self.backend.start()

        self.backend.join()

if __name__ == '__main__':
    mediator = Mediator()
    mediator.start_communication()
    
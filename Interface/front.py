from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.core.window import Window
Window.size = (500,500)
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

BUTTON_WIDTH = 70
BUTTON_HEIGHT= 40

class Contacts_Generator_UI_wrapper:
    def __init__(self, api):
        self.api = api

    def run(self):
        Contacts_Generator_UI().run()


class Contacts_Generator_UI(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(None, None), width=500, height=500)
        self.root.canvas.before.clear()
        with self.root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Set backgroud color to (.9,.9,.9,1)
            self.rect = Rectangle(size=self.root.size, pos=self.root.pos)
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200, padding=[0, 10, 0, 10])
        input_layout.add_widget(Label(text='Keywords', size_hint_y=None, height=30, size_hint_x=None, width=100))
        self.keywords_input = TextInput(multiline=False, size_hint_y=None, height=30)
        input_layout.add_widget(self.keywords_input)

        input_layout.add_widget(Label(text='Channel', size_hint_y=None, height=30, size_hint_x=None, width=100))
        self.channel_input = TextInput(multiline=False, size_hint_y=None, height=30)
        input_layout.add_widget(self.channel_input)

        input_layout.add_widget(Label(text='Min Count', size_hint_y=None, height=30, size_hint_x=None, width=100))
        self.mincount_input = TextInput(multiline=False, size_hint_y=None, height=30)
        input_layout.add_widget(self.mincount_input)

        # Settings button
        settings_btn = Button(text='Settings', size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        settings_btn.bind(on_press=self.open_settings_popup)
        self.root.add_widget(settings_btn)
    
        # Adding the GridLayout to the root layout
        self.root.add_widget(input_layout)
        
        # Spacer Widget - This pushes everything to the top
        spacer = Widget(size_hint_y=1)
        self.root.add_widget(spacer)

        # Configuration Tab
        config_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
        config_layout.add_widget(Label(text='Configuration Progress', size_hint_y=None, height=30))
        config_layout.add_widget(self.progress_bar)
        self.root.add_widget(config_layout)

        # Start Button
        start_button = Button(text='Start Scraping', on_press=self.start_scraping, size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.root.add_widget(start_button)
        
        return self.root

    def start_scraping(self, instance):
        # Start configuration simulation
        self.progress_bar.value = 0
        Clock.schedule_interval(self.simulate_loading, 0.1)

    def simulate_loading(self, dt):
        self.progress_bar.value += 1
        if self.progress_bar.value >= 100:
            Clock.unschedule(self.simulate_loading)
            self.show_scraping_popup()

    def show_scraping_popup(self):
        keywords = self.keywords_input.text
        channel = self.channel_input.text
        mincount = self.mincount_input.text
        max_tasks = self.max_tasks_input.text
        file_name = self.file_name_input.text
        file_path = self.file_chooser.path

        # Simulate scraping process
        popup = Popup(title='Scraping Started',
                      content=Label(text=f'Scraping with:\nKeywords: {keywords}\nChannel: {channel}\nMin Count: {mincount}\nMax Tasks: {max_tasks}\nFile: {file_path}/{file_name}'),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def open_settings_popup(self, instance):
        # Popup content layout
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text='Settings', font_size='20sp', bold=True, size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH))

        # File Name input
        file_name_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=50, padding=[0, 10, 0, 10])
        file_name_layout.add_widget(Label(text='File Name', size_hint_x=None, width=100))
        self.file_name_input = TextInput(text='', multiline=False, size_hint_y=None, height=30, readonly=True)
        file_name_layout.add_widget(self.file_name_input)
        file_chooser_button = Button(text='Choose File', size_hint_x=None, width=100)
        file_chooser_button.bind(on_press=self.open_file_chooser)
        file_name_layout.add_widget(file_chooser_button)
        content.add_widget(file_name_layout)

        # Max Tasks input
        max_tasks_layout = GridLayout(cols=3, spacing=10, size_hint_y=None, height=50, padding=[0, 10, 0, 10])
        max_tasks_layout.add_widget(Label(text='Max Tasks', size_hint_x=None, width=100))
        self.max_tasks_input = TextInput(text='', multiline=False, size_hint_y=None, height=30)
        max_tasks_layout.add_widget(self.max_tasks_input)
        content.add_widget(max_tasks_layout)

        # Save button
        save_btn = Button(text='Save', size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        save_btn.bind(on_press=lambda x: self.save_settings(self.file_name_input.text, self.max_tasks_input.text))
        content.add_widget(save_btn)

        # Create and open popup
        self.settings_popup = Popup(title='', content=content, size_hint=(None, None), size=(400, 250))
        self.settings_popup.open()

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(dirselect=True, size_hint_y=0.9)
        submit_btn = Button(text='Submit', size_hint_y=None, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)

        # Add file chooser and submit button to the layout
        content.add_widget(file_chooser)
        content.add_widget(submit_btn)

        # Create the file chooser popup
        popup = Popup(content=content, title="Choose a directory", size_hint=(0.9, 0.9), auto_dismiss=False)

        # Bind the submit button to both select the file and dismiss the popup
        submit_btn.bind(on_press=lambda x: self.select_file(file_chooser, file_chooser.selection, None))
        submit_btn.bind(on_press=lambda x: popup.dismiss())

        # Prevent the settings popup from being dismissed while this popup is open
        self.settings_popup.auto_dismiss = False

        # Ensure the settings popup can be dismissed again after closing this popup
        popup.bind(on_dismiss=lambda x: setattr(self.settings_popup, 'auto_dismiss', True))

        popup.open()

    def select_file(self, filechooser, selection, touch):
        # Check if the selectgion is a dir and not a file
        if selection:
            selected = selection[0]
            if os.path.isdir(selected):
                # If the selection is a directory, use it directly
                self.file_name_input.text = selected+"\\"
            else:
                # If the selection is not a directory, find its parent directory
                parent_dir = os.path.dirname(selected)+"\\"
                self.file_name_input.text = parent_dir

    def save_settings(self, file_name, max_tasks):
        # Here you would save the settings
        pass

if __name__ == '__main__':
    Contacts_Generator_UI().run()
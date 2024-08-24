from google.colab import drive
import libtorrent as lt
import time
import sys
import warnings
from usellm import UseLLM, Message, Options

def authenticate_google():
    drive.mount('/content/drive')
    print("Google Drive has been connected!")

def download_from_magnet(link, save_path=None):
    if not save_path:
        save_path = '/content/downloads/'  # Default save path if not specified

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Ignore deprecation warnings

        ses = lt.session()
        params = {
            'save_path': save_path,
            'storage_mode': lt.storage_mode_t(2),
        }

        handle = lt.add_magnet_uri(ses, link, params)
        ses.start_dht()

        while not handle.has_metadata():
            time.sleep(1)

        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            sys.stdout.write(f'\rProgress: {s.progress * 100:.2f}% - Download Speed: {s.download_rate / 1000:.2f} KB/s')
            sys.stdout.flush()
            time.sleep(1)

        info = handle.get_torrent_info()
        files = info.files()
        file_list = [files.file_path(i) for i in range(files.num_files())]  # Get the list of all file paths
        downloaded_file = save_path + file_list[0]  # Assuming the first file in the list is what you need

        print('\nDownload complete!')
        print(f"Downloaded file: {downloaded_file}")

def torrent_downloader(magnet_link, save_path=None):
    if save_path == 'google':
        authenticate_google()
        save_path = '/content/drive/My Drive/'  # Set default Google Drive directory
    else:
        save_path = save_path if save_path else '/content/downloads/'  # Default save path if not provided

    download_from_magnet(magnet_link, save_path)

MAX_HISTORY_LENGTH = 1000
conversation_history = []

def ask(message):
    global conversation_history
    service = UseLLM(service_url="https://usellm.org/api/llm")
    conversation_history.append(Message(role="user", content=message))
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        trim_length = int(len(conversation_history) * 0.25)
        conversation_history = conversation_history[trim_length:]
    if len(conversation_history) == 1:
        print("നമസ്കാരം ")
    options = Options(messages=conversation_history)
    response = service.chat(options)
    conversation_history.append(Message(role="assistant", content=response.content))

    print(response.content)

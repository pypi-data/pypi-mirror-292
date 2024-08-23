import YWP.Audios as Audios
import pyttsx3
import subprocess
import YWP.Files as Files
import YWP.Websites as Websites
import YWP.Crypto as Crypto
import YWP.VideosCreator as VideosCreator
import YWP.endecrypt as endecrypt
import YWP.Libraries as Libraries
import platform
import sys
import os
from time import sleep
from sys import stdout
from googletrans import Translator
from flask import Flask
import YWP.AskAI as AskAI

apps = None

class Audios_inuser:
    def play_sound_inuser():
        filename = input("Enter FileName: ")
        return Audios.play_sound(filename)
    
    def play_audio_inuser():
        pro_path = input("Enter Program Path: ")
        mp3_file_path = input("Enter MP3 File Path: ")
        return Audios.play_audio(pro_path, mp3_file_path)
        
    def record_audio_inuser():
        filename = input("Enter FileName [recorder.wav]: ")
        if filename == "":
            filename = "recorder.wav"
        return Audios.record_audio(filename)
    
    def transcribe_audio_inuser():
        filename = input("Enter FileName [recorder.wav]: ")
        if filename == "":
            filename = "recorder.wav"
        return Audios.transcribe_audio(filename)
            
    def text_to_speech_inuser():
        text = input("Enter Text: ")
        filename = input("Enter FileName [tts.mp3]: ")
        if filename == "":
            filename = "tts.mp3"
        return Audios.text_to_speech(text, filename)
    
    def text_to_speech_offline_inuser():
        text = input("Enter Text: ")
        filename = input("Enter FileName [tts.mp3]: ")
        if filename == "":
            filename = "tts.mp3"
        engine = pyttsx3.init()
        engine.save_to_file(text, filename)
        engine.runAndWait()
        return "saved"
    
    def play_audio_online_inuser():
        pro_path = input("Enter Program Path: ")
        mp3_file_link = input("Enter MP3 File Link: ")
        subprocess.Popen([pro_path, mp3_file_link])
        return "opened"
    
class Files_inuser:
    def create_file_inuser():
        name = input("Enter FileName: ")
        return Files.create_file(name)
        
    def open_file_inuser():
        filepath = input("Enter FilePath: ")
        return Files.open_file(filepath)
        
    def delete_all_files_inuser():
        directory = input("Enter Directory/Folder [.]: ")
        if directory == "":
            directory = "."
        type = input("Enter Type: ")
        return Files.delete_all_files(directory, type)
                    
    def delete_file_inuser():
        filepath = input("Enter FilePath: ")
        return Files.delete_file(filepath)
                    
class Websites_inuser:
    
    def open_website_inuser():
        url = input("Enter URL: ")
        return Websites.open_website(url)
        
class Crypto_inuser:

    def token_information_inuser():
        data = input("Enter Data: ")
        type = input("Enter Type [binance]: ")
        if type == "":
            type = "binance"
        return Crypto.token_information(data, type)
        
class server_inuser:

    def route_flask_inuser():
        global apps
        
        location = input("Enter Location [.]: ")
        if location == "":
            location = "."
        returnValue = input("Enter returnValue: ")

        app = apps
        try:
            if app is None:
                app = Flask(__name__)

            def make_route(return_value):
                def route():
                    return return_value
                return route

            endpoint = location.strip('/')
            if endpoint == '':
                endpoint = 'index'

            app.add_url_rule(location, endpoint, make_route(returnValue))
            apps = app
            return 'done'
        except Exception as error:
            raise error
        
    def run_inuser():
        global apps
        
        check = input("Enter check [False]: ")
        if check == "":
            check = False
        else:
            check = bool(check)
        debug = input("Enter Debug [True]: ")
        if debug == "":
            debug = True
        else:
            debug = bool(debug)
        host = input("Enter Host [0.0.0.0]: ")
        if host == "":
            host = "0.0.0.0"
        port = input("Enter Port [8000]: ")
        if port == "":
            port = "8000"
        
        app = apps
        try:
            if app is None:
                raise Exception("App not initialized")
            
            if check:
                if __name__ == "__main__":
                    app.run(debug=debug, host=host, port=port)
            else:
                app.run(debug=debug, host=host, port=port)
            return 'done'
        except Exception as error:
            raise error
        
# class AI:
#     class Builder:
#         def __init__(self):
#             self.intents = []
            
#         def json_creator_inuser(self):
#             jsonfile = input("Enter JsonFile Name/Path [intents.json]: ")
#             if jsonfile == "":
#                 jsonfile = "intents.json"
#             tag = input("Enter tag: ")
#             patterns = input("Enter Patterns (,): ").split(",")
#             responses = input("Enter Responses (,): ").split(",")
#             intents = self.intents

#             intents.append({
#                 "tag": tag,
#                 "patterns": patterns,
#                 "responses": responses
#             })

#             with open(jsonfile, 'w', encoding='utf-8') as f:
#                 json.dump({"intents": intents}, f, indent=4, ensure_ascii=False)

#         def train_inuser(self):
#             jsonfile = input("Enter JsonFile Name/Path [intents.json]: ")
#             if jsonfile == "":
#                 jsonfile = "intents.json"
#             picklefile = input("Enter PickleFile Name/Path [data.pickle]: ")
#             if picklefile == "":
#                 picklefile = "data.pickle"
#             h5file = input("Enter H5File Name/Path [model.h5]: ")
#             if h5file == "":
#                 h5file = "model.h5"

#             nltk.download('punkt')
#             stemmer = LancasterStemmer()

#             try:
#                 with open(jsonfile, encoding='utf-8') as file:
#                     data = json.load(file)
#             except:
#                 return 'error:jsonnotfound'

#             try:
#                 with open(picklefile, "rb") as f:
#                     words, labels, training, output = pickle.load(f)
#             except:
#                 words = []
#                 labels = []
#                 docs_x = []
#                 docs_y = []
#                 for intent in data["intents"]:
#                     for pattern in intent["patterns"]:
#                         wrds = nltk.word_tokenize(pattern)
#                         words.extend(wrds)
#                         docs_x.append(wrds)
#                         docs_y.append(intent["tag"])

#                     if intent["tag"] not in labels:
#                         labels.append(intent["tag"])

#                 words = [stemmer.stem(w.lower()) for w in words if w != "?"]
#                 words = sorted(list(set(words)))

#                 labels = sorted(labels)

#                 training = []
#                 output = []

#                 out_empty = [0 for _ in range(len(labels))]

#                 for x, doc in enumerate(docs_x):
#                     bag = []

#                     wrds = [stemmer.stem(w) for w in doc]

#                     for w in words:
#                         if w in wrds:
#                             bag.append(1)
#                         else:
#                             bag.append(0)

#                     output_row = out_empty[:]
#                     output_row[labels.index(docs_y[x])] = 1

#                     training.append(bag)
#                     output.append(output_row)

#                 training = np.array(training)
#                 output = np.array(output)

#                 with open(picklefile, "wb") as f:
#                     pickle.dump((words, labels, training, output), f)

#             model = Sequential()
#             model.add(Dense(8, input_shape=(len(training[0]),), activation='relu'))
#             model.add(Dense(8, activation='relu'))
#             model.add(Dense(len(output[0]), activation='softmax'))

#             model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#             try:
#                 model.load_weights(h5file)
#             except:
#                 model.fit(training, output, epochs=1000, batch_size=8, verbose=1)
#                 model.save(h5file)

#             return 'done'

#         def process_inuser(self):
#             message = input("Enter Message: ")
#             picklefile = input("Enter PickleFile Name/Path [data.pickle]: ")
#             if picklefile == "":
#                 picklefile = "data.pickle"
#             h5file = input("Enter H5File Name/Path [model.h5]: ")
#             if h5file == "":
#                 h5file = "model.h5"
#             jsonfile = input("Enter JsonFile Name/Path [intents.json]: ")
#             if jsonfile == "":
#                 jsonfile = "intents.json"
#             sleeptime = input("Enter Sleep Time [0]: ")
#             if sleeptime == "":
#                 sleeptime = 0
#             else:
#                 sleeptime = int(sleeptime)
                
#             nltk.download('punkt')
#             stemmer = LancasterStemmer()

#             try:
#                 with open(jsonfile, encoding='utf-8') as file:
#                     data = json.load(file)
#             except:
#                 return 'error:jsonnotfound'

#             try:
#                 with open(picklefile, "rb") as f:
#                     words, labels, training, output = pickle.load(f)
#             except:
#                 return 'error:picklenotfound'

#             model = Sequential()
#             model.add(Dense(8, input_shape=(len(training[0]),), activation='relu'))
#             model.add(Dense(8, activation='relu'))
#             model.add(Dense(len(output[0]), activation='softmax'))

#             model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

#             try:
#                 model.load_weights(h5file)
#             except:
#                 return 'h5notfound'

#             ai = AI.Builder()
#             bag = ai.bag_of_words(message, words)
#             results = model.predict(np.array([bag]))[0]
#             results_index = np.argmax(results)
#             tag = labels[results_index]
#             if results[results_index] > 0.8:
#                 for tg in data["intents"]:
#                     if tg['tag'] == tag:
#                         responses = tg['responses']
#                 sleep(sleeptime)
#                 Bot = random.choice(responses)
#                 return Bot
#             else:
#                 return "I don't understand!"

class VideosCreator_inuser:

    class Basic_inuser:
        
        def basic_video_creator_inuser():
            image_folder = input("Enter Image Folder Name/Path [images]: ")
            if image_folder == "":
                image_folder = "images"
            animation_choice = input("Enter Animation [None]: ")
            if animation_choice == "":
                animation_choice = "None"
            frame_rate = input("Enter Frame Rate [25]: ")
            if frame_rate == "":
                frame_rate = 25
            else:
                frame_rate = int(frame_rate)
            video_name = input("Enter Video Name: ")
            video_type = input("Enter Video Type [mp4]: ")
            if video_type == "":
                video_type = "mp4"
            video_platform = input("Enter Video Platform [Youtube]: ")
            if video_platform == "":
                video_platform = "Youtube"
            image_time = input("Enter Image Time [5]: ")
            if image_time == "":
                image_time = 5
            else:
                image_time = int(image_time)
            return VideosCreator.Basic.basic_video_creator(image_folder, animation_choice, frame_rate, video_name, video_type, video_platform, image_time)
        
class endecrypt_inuser:

    class aes_inuser:
        def encrypt_inuser():
            file_path = input("Enter File Path: ")
            password = input("Enter Password: ")
            
            return endecrypt.aes.encrypt(file_path, password)

        def decrypt_inuser():
            file_path = input("Enter File Path: ")
            password = input("Enter Password: ")
            
            return endecrypt.aes.decrypt(file_path, password)

    class BlowFish_inuser:
        def encrypt_inuser():
            file_path = input("Enter File Path: ")
            password = input("Enter Password: ")
            
            return endecrypt.BlowFish.encrypt(file_path, password)

        def decrypt_inuser():
            file_path = input("Enter File Path: ")
            password = input("Enter Password: ")
            
            return endecrypt.BlowFish.decrypt(file_path, password)

    class Base64_inuser:
        def encrypt_inuser():
            file_path = input("Enter File Path: ")
            
            return endecrypt.Base64.encrypt(file_path)
            
        def decrypt_inuser():
            file_path = input("Enter File Path: ")
            
            return endecrypt.Base64.decrypt(file_path)
            
    class Hex_inuser:
        def encrypt_inuser():
            file_path = input("Enter File Path: ")
            
            return endecrypt.Hex.encrypt(file_path)
            
        def decrypt_inuser():
            file_path = input("Enter File Path: ")
            
            return endecrypt.Hex.decrypt(file_path)
            
class Libraries_inuser:

    class Basic_inuser:
        def init_creator_inuser():
            filesave = input("Enter File Save [__init__.py]: ")
            if filesave == "":
                filesave = "__init__.py"
            filename = input("Enter File Name: ")
            function_class = input("Enter Function/Class Name: ")
            
            return Libraries.Basic.init_creator(filesave, filename, function_class)
                
        def basic_setup_file_creator_inuser():
            filename = input("Enter File Name [setup.py]: ")
            if filename == "":
                filename = "setup.py"
            folder_name = input("Enter Folder Name: ")
            readme_name = input("Enter Read Me File Name [README.md]: ")
            if readme_name == "":
                readme_name = "README.md"
            library_name = input("Enter Library Name: ")
            library_version = input("Enter Library Version: ")
            libraries_required = input("Enter Libraries Required (,): ").split(",")
            description = input("Enter Description: ")
            creator_name = input("Enter Creator Name: ")
            creator_email = input("Enter Creator Email: ")
            License = input("Enter License [MIT]: ")
            if License == "":
                License = "MIT"
            else:
                return 'Not From Licenses'
            
            return Libraries.Basic.basic_setup_file_creator(filename, folder_name, readme_name, library_name, library_version, libraries_required, description, creator_name, creator_email, License)
                    
        def upload_file_creator_inuser():
            filename = input("Enter File Name [upload_library]: ")
            if filename == "":
                filename = "upload_library"
            pypi_api = input("Enter PyPi API: ")
            platform = input("Enter Platform: ")
            
            return Libraries.Basic.upload_file_creator(filename, pypi_api, platform)

def install_system_packages():
    system = platform.system()
    
    if system == 'Linux':
        command = 'sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-pyaudio libasound2-dev libportaudio2 libportaudiocpp0'
    elif system == 'Darwin':
        command = 'brew install portaudio'
    elif system == 'Windows':
        command = f'{sys.executable} -m pip install pipwin && {sys.executable} -m pipwin install pyaudio'
    else:
        return "Unsupported OS"
    
    run_command(command)
    return "Done"

def install_library_packages():
    libraries=[
        "dill==0.3.8",
        "flask==3.0.3",
        "flask-cors==4.0.1",
        "gtts==2.5.1",
        "joblib==1.4.2",
        "moviepy==1.0.3",
        "nltk==3.8.1",
        "pyaudio==0.2.14",
        "pygame==2.5.2",
        "selenium==4.22.0",
        "setuptools==68.1.2",
        "sounddevice==0.4.7",
        "SpeechRecognition==3.10.4",
        "tensorflow==2.16.1",
        "tflearn==0.5.0",
        "twine==5.1.0",
        "wheel==0.43.0",
        "pycryptodome==3.20.0",
        "vosk==0.3.45",
        "tqdm==4.66.4",
        "pyttsx3==2.90",
        "requests==2.31.0",
        "googletrans==4.0.0rc1",
        "cryptography==42.0.5",
        "scapy==2.5.0+git20240324.2b58b51",
        "python-nmap==0.7.1",
        "yara-python==4.5.1",
        "pillow==10.4.0",
    ]

    command = "pip install "
    for library in libraries:
        command += str(library) + " "
    run_command(command)
    
    return 'Done'

def upgrade_required_libraries():
    libraries=[
        "dill",
        "flask",
        "flask-cors",
        "gtts",
        "joblib",
        "moviepy",
        "nltk",
        "pyaudio",
        "pygame",
        "selenium",
        "setuptools",
        "sounddevice",
        "SpeechRecognition",
        "tensorflow",
        "tflearn",
        "twine",
        "wheel",
        "pycryptodome",
        "vosk",
        "tqdm",
        "pyttsx3",
        "requests",
        "googletrans",
        "cryptography",
        "scapy",
        "python-nmap",
        "yara-python",
        "pillow",
    ]
    
    command = "pip install --upgrade "
    for library in libraries:
        command += library + " "
    run_command(command)
    
    return 'Done'

def upgrade_library():
    command = "pip install --upgrade YWP"
    run_command(command)
    
    return 'Done'

def get_terminal_command():
    if sys.platform.startswith('win'):
        return "cmd.exe"
    elif sys.platform.startswith('linux'):
        terminals = ["gnome-terminal", "xterm", "konsole", "xfce4-terminal", "lxterminal", "terminator", "tilix", "mate-terminal"]
        available_terminals = [term for term in terminals if os.system(f"which {term} > /dev/null 2>&1") == 0]
        if available_terminals:
            return available_terminals[0]
        else:
            return None
    elif sys.platform.startswith('darwin'):
        return "Terminal"
    else:
        return None

def run_command(command):
    terminal = get_terminal_command()
    if terminal:
        if terminal == "cmd.exe":
            os.system(f'start cmd /c "{command}"')
        elif terminal in ["gnome-terminal", "terminator", "tilix"]:
            os.system(f"{terminal} -- bash -c '{command}; read -p \"Press Enter to close...\"'")
        elif terminal == "konsole":
            os.system(f"{terminal} -e 'bash -c \"{command}; read -p \\\"Press Enter to close...\\\"\"'")
        elif terminal == "Terminal":
            os.system(f"open -a {terminal} '{command}'")
        else:
            os.system(f"{terminal} -hold -e 'bash -c \"{command}; read -p \\\"Press Enter to close...\\\"\"'")
    else:
        return "No supported terminal found."

def install_packages_linux_inuser():
    system = platform.system()
    
    if system == 'Linux':
        command = 'sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-pyaudio libasound2-dev libportaudio2 libportaudiocpp0'
    elif system == 'Darwin':
        command = 'brew install portaudio'
    elif system == 'Windows':
        command = f'{sys.executable} -m pip install pipwin && {sys.executable} -m pipwin install pyaudio'
    else:
        return "Unsupported OS"
    
    run_command(command)
    return "Done"

def install_libraries_inuser():
    libraries=[
        "dill==0.3.8",
        "flask==3.0.3",
        "flask-cors==4.0.1",
        "gtts==2.5.1",
        "joblib==1.4.2",
        "moviepy==1.0.3",
        "nltk==3.8.1",
        "pyaudio==0.2.14",
        "pygame==2.5.2",
        "selenium==4.22.0",
        "setuptools==68.1.2",
        "sounddevice==0.4.7",
        "SpeechRecognition==3.10.4",
        "tensorflow==2.16.1",
        "tflearn==0.5.0",
        "twine==5.1.0",
        "wheel==0.43.0",
        "pycryptodome==3.20.0",
        "vosk==0.3.45",
        "tqdm==4.66.4",
        "pyttsx3==2.90",
        "requests==2.31.0",
        "googletrans==4.0.0rc1",
        "cryptography==42.0.5",
        "scapy==2.5.0+git20240324.2b58b51",
        "python-nmap==0.7.1",
        "yara-python==4.5.1",
        "pillow==10.4.0",
    ]

    command = "pip install --upgrade "
    for library in libraries:
        command += str(library) + " "
    run_command(command)
    
    return 'Done'

def upgrade_libraries_inuser():
    libraries=[
        "dill",
        "flask",
        "flask-cors",
        "gtts",
        "joblib",
        "moviepy",
        "nltk",
        "pyaudio",
        "pygame",
        "selenium",
        "setuptools",
        "sounddevice",
        "SpeechRecognition",
        "tensorflow",
        "tflearn",
        "twine",
        "wheel",
        "pycryptodome",
        "vosk",
        "tqdm",
        "pyttsx3",
        "requests",
        "googletrans",
        "cryptography",
        "scapy",
        "python-nmap",
        "yara-python",
        "pillow",
    ]
    
    command = "pip install --upgrade "
    for library in libraries:
        command += library + " "
    run_command(command)
    
    return 'Done'

def upgrade_library_inuser():
    command = "pip install --upgrade YWP"
    run_command(command)
    
    return 'Done'

class printstyle_inuser:
    def print_one_inuser():
        
        text = input("Enter Text: ")
        second = input("Enter Second [0.05]: ")
        if second == "":
            second = 0.05
        else:
            second = float(second)
        
        if len(text) == 0:
            raise ZeroDivisionError
        
        for line in text + '\n':
            stdout.write(line)
            stdout.flush()
            sleep(second)
        
    def print_all_inuser():
        
        text = input("Enter Text: ")
        total_time = input("Enter Total Time [5]: ")
        if total_time == "":
            total_time = 5
        else:
            total_time = float(total_time)
        
        # حساب الوقت الفاصل بين كل حرف
        if len(text) == 0:
            raise ZeroDivisionError
        else:
            interval = total_time / len(text)
        
        # طباعة النص حرفًا بحرف
        for char in text:
            stdout.write(char)
            stdout.flush()
            sleep(interval)
        
        # طباعة سطر جديد بعد انتهاء النص
        stdout.write('\n')
        stdout.flush()
        
class Translate_inuser:
    def translate_text_inuser():
        text = input("Enter Text: ")
        to_lan = input("Enter To Language [en]: ")
        if to_lan == "":
            to_lan = "en"
        from_lan = input("Enter From Language [en]: ")
        if from_lan == "":
            from_lan = "en"
        translator = Translator()
        return translator.translate(text, src=from_lan, dest=to_lan).text

class AskAI_inuser:
    class YWPAI_inuser:
        def BetaVersion_inuser():
            query = input("Enter Query: ")
            Name = input("Enter Your Name (optional): ")
            os = input("Enter Your OS (optional): ")
            Country = input("Enter Your Country (optional): ")
            Work = input("Enter Where are you Work (optional): ")
            Company = input("Enter Your Company Name (If Available) (optional): ")
            return AskAI.YWPAI.BetaVersion(query, Name, os, Country, Work, Company)

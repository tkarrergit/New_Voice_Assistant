import time
import App_Gui.gui as gui
import sys
import App_Utilitys.shared as shared
import App_Utilitys.video as video
import threading
from pynput import keyboard
import re
import App_Speech.vosk_functions as vosk_functions
import App_Speech.speech as speech
import App_Utilitys.utilitys as utilitys
from hugchat import hugchat
from hugchat.login import Login

def initialize_hugchat(email, passwd):    
    try:
        print("initialize_hugchat: " + email + passwd)
        # Cookies im lokalen Verzeichnis speichern
        cookie_path_dir = (utilitys.resource_path("./cookies_snapshot")   )         
        # Einloggen bei Huggingface und Autorisieren von HugChat
        sign = Login(email, passwd)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        
        # Create your ChatBot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

        return chatbot
    except Exception as e:
        print(f"Fehler bei der Initialisierung von Huggingface: {e}")
        return None


def hugchat_assistent(chatbot, user_input, new_conversation):  
    if user_input:  
        
        starttime = time.time()
        antwort = chatbot.chat(user_input, conversation = new_conversation)
        print("Hallo")    
        print(str(antwort))
        print("Hallo2")
        endtime = time.time()
        duration = endtime -starttime
        print(duration)
        return antwort 
    else:
        antwort = "Leider keinen Input erkannt"
        return antwort 

def hugchat_initialize(email, passwort, assistant, engine):
        try:
            chatbot = initialize_hugchat(email, passwort)
            tomconversation = chatbot.new_conversation(assistant=assistant) 
            return tomconversation, chatbot
        except Exception as e:
            speech.text_to_speech(engine, "Anmeldung fehlgeschlagen. Bitte starten sie die App neu und überprüfen sie ihre Anmeldedaten.")            

def hugchat_initialize_no_assistant(email, passwort, engine):
    try:
        chatbot = initialize_hugchat(email, passwort)
        tomconversation = chatbot.new_conversation() 
        return tomconversation, chatbot
    except Exception as e:
        print("Anmeldung fehlgeschlagen. Bitte starten sie die App neu und überprüfen sie ihre Anmeldedaten.") 
        speech.text_to_speech("Anmeldung fehlgeschlagen. Bitte starten sie die App neu und überprüfen sie ihre Anmeldedaten.")        

def hugchat_assistent_stream(chatbot, user_input, newconversation, page):
    try:           
        sprich_stream_chat_satz(chatbot, user_input, newconversation, page)
    except:
        print("No Input")

def sprich_stream_chat_satz_old(chatbot, user_input, conversation):
    # Spricht jeden vollständigen Satz der Antwort einen nach dem anderen.
    full_response = ""
    current_sentence = ""
    
    try: 
        for resp in chatbot._stream_query(user_input, conversation=conversation):
            if resp is not None and resp.get('type') == 'stream':
                token = resp['token']
                current_sentence += token

                # Bereinige den aktuellen Satz von NULL-Zeichen und Sternchen
                current_sentence = re.sub(r'[\x00*•]', '', current_sentence)  # Remove NULL characters and '*'
                
                # Überprüfe, ob der aktuelle Token mit einem Satzzeichen endet
                if re.search(r'[.!?]', token):
                    # Sprich den vollständigen Satz
                    print(current_sentence)
                    full_response += current_sentence
                    
                    if vosk_functions.stop_flag == False:
                        video.play(video.videos[0])
                        speech.text_to_speech(current_sentence)
                        video.pause(video.videos[0]) 
                        video.seek(video.videos[0])

                    current_sentence = ""

        # Falls der letzte Satz kein Satzzeichen hatte, trotzdem sprechen
        if current_sentence:
            current_sentence = re.sub(r'[\x00*•]', '', current_sentence)  # Remove NULL characters and '*'
            speech.text_to_speech(current_sentence)

    except Exception as e:
        print(f"ERROR: {e}")
        stimme = shared.stimme
        speech.text_to_speech("Dein Klient ist gerade nicht erreichbar....versuch es gleich nochmal....")

def sprich_stream_chat_satz(chatbot, user_input, conversation, page):
    global stop_reading_event, counter, stop_writing_event
    listener_running = True  # Variable zum Beenden des Listeners
    stop_reading_event = threading.Event()
    stop_writing_event = threading.Event()

    # Zähler für Backspace-Tastendrücke
    counter = 0

    def on_press(key):
        global counter
        if key == keyboard.Key.backspace:
            counter += 1
            print(f"Vorlesen abgebrochen. Backspace-Zähler: {counter}")
            stop_reading_event.set()  # Setzt das Event zum Stoppen des Vorlesens
            if counter >= 2:
                stop_writing_event.set()  # Setzt das Event zum Stoppen des Schreibens
            # Beende den Listener erst, wenn zwei Backspace-Tastendrücke erreicht sind
            return counter < 2

    def check_escape_key():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    # Starte den Listener in einem eigenen Thread
    escape_thread = threading.Thread(target=check_escape_key, daemon=True)
    escape_thread.start()

    # Initialisiere eine leere Zeichenkette für den zusammenhängenden Text    
    full_response = ""
    current_sentence = ""

    try:
        for resp in chatbot._stream_query(
            user_input,
            conversation=conversation,
        ):
            # Überprüfen, ob Backspace zweimal gedrückt wurde
            if stop_writing_event.is_set():
                print("Schreiben und Vorlesen abgebrochen nach zwei Backspace.")
                break

            if resp is not None and resp.get('type') == 'stream':
                token = resp['token']
                current_sentence += token
                current_sentence = re.sub(r'[\x00*•]', '', current_sentence)  # Bereinigen von Sonderzeichen

                # Überprüfen, ob das aktuelle Token ein Satzende ist
                if re.search(r'[.!?]', token):
                    cleaned_sentence = re.sub(r'\x00', '', current_sentence)
                    print(cleaned_sentence, end=" ")
                    sys.stdout.flush()
                    full_response += cleaned_sentence
                    print(f"full_response: {full_response}")
                    gui.update_response_text(page, shared.response_text, full_response)

                    if not stop_reading_event.is_set() and not vosk_functions.stop_flag:
                        speech.text_to_speech(cleaned_sentence)

                    current_sentence = ""

        # Falls der letzte Satz kein Satzzeichen hatte, trotzdem sprechen
        if current_sentence and not stop_writing_event.is_set():
            current_sentence = re.sub(r'[\x00*•]', '', current_sentence)  # Bereinigen von Sonderzeichen
            speech.text_to_speech(current_sentence)

    except Exception as e:
        print(f"ERROR: {e}")

def sprachsteuerung(page):
    while True:
        user_input = vosk_functions.get_user_input(shared.vosk_recognizer, page)
        sprich_stream_chat_satz(shared.chatbot, user_input, shared.conversation, page)

#engine = pyttsx3.init()
#sprachsteuerung(engine)
            
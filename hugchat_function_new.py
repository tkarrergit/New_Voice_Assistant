from hugchat import hugchat
from hugchat.login import Login

def initialize_hugchat(email, passwd):    
    try:
        print("initialize_hugchat: " + email + passwd)
        # Cookies im lokalen Verzeichnis speichern
        cookie_path_dir = ("./cookies_snapshot")           
        # Einloggen bei Huggingface und Autorisieren von HugChat
        sign = Login(email, passwd)
        cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
        
        # Create your ChatBot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

        return chatbot
    except Exception as e:
        print(f"Fehler bei der Initialisierung von Huggingface: {e}")
        return None

def hugchat_initialize_no_assistant(email, passwort):
    try:
        chatbot = initialize_hugchat(email, passwort)
        tomconversation = chatbot.new_conversation() 
        return tomconversation, chatbot
    except Exception as e:
        print("Anmeldung fehlgeschlagen. Bitte starten sie die App neu und überprüfen sie ihre Anmeldedaten.")          
        
def hugchat_assistent(chatbot, user_input, new_conversation): 
    chatbot.switch_llm(6)
    if user_input:                 
        antwort = chatbot.chat(user_input, conversation = new_conversation)          
        print(str(antwort))                
        return antwort 
    else:
        antwort = "Leider keinen Input erkannt"
        return antwort 

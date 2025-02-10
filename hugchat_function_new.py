from hugchat import hugchat
from hugchat.login import Login


def model_auswahl(chatbot, model_name=None, model_index=None):
    """
    Wählt ein LLM-Modell aus und aktiviert es direkt im ChatBot
    
    Parameter:
    - model_name: Direkte Auswahl per Modellnamen (Priorität 1)
    - model_index: Direkte Auswahl per Index (Priorität 2)
    
    Rückgabewerte: (modell_name, modell_index)
    """
    models = chatbot.get_available_llm_models()
    
    # Direkte Modellauswahl per Name
    if model_name:
        if model_name in models:
            index = models.index(model_name)
            chatbot.switch_llm(index)
            return models[index], index
        raise ValueError(f"Modell '{model_name}' nicht verfügbar")

    # Direkte Indexauswahl
    if model_index is not None:
        if 0 <= model_index < len(models):
            chatbot.switch_llm(model_index)
            return models[model_index], model_index
        raise ValueError(f"Ungültiger Index {model_index}")

    # Interaktive Auswahl
    print("Verfügbare Modelle:")
    for idx, modell in enumerate(models):
        print(f"[{idx}] {modell}")
    
    while True:
        try:
            index = int(input("\nModellindex: "))
            if 0 <= index < len(models):
                chatbot.switch_llm(index)
                print(f"Aktives Modell: {models[index]}")
                return models[index], index
            print(f"Index 0-{len(models)-1} eingeben!")
        except ValueError:
            print("Numerischen Index eingeben")


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
        print("Anmeldung fehlgeschlagen. Bitte starten sie die App neu und überprüfen sie ihre Anmeldedaten oder ihren Internetzugang.")          
        
def hugchat_assistent(chatbot, user_input, new_conversation): 
    chatbot.switch_llm(6)
    if user_input:                 
        antwort = chatbot.chat(user_input, conversation = new_conversation)          
        print(str(antwort))                
        return antwort 
    else:
        antwort = "Leider keinen Input erkannt"
        return antwort 


email="sand.burg@mail.de"
passwd = "Heckmeck16!"
input_text = "Hallo wie heißt dein llm Modell?"
chatbot = initialize_hugchat(email, passwd)
#modell, index = model_auswahl(chatbot)
#conversation = chatbot.new_conversation() 
antwort = chatbot.chat(input_text, model_index=4)
antwort_str: str = antwort.wait_until_done()

#antwort = hugchat_assistent(chatbot, input_text, new_conversation)
result = str(antwort_str)
print(result)

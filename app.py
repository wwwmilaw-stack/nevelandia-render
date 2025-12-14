from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import os

# --------------------
# CONFIG
# --------------------

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Memoria conversazioni (per demo va bene)
conversazioni = {}

# --------------------
# SYSTEM PROMPT
# --------------------

# ---- SISTEMA ASSISTENTE NEVELANDIA ----
SYSTEM_PROMPT = """
Sei l'assistente ufficiale di Nevelandia, il parco giochi sulla neve.
Rispondi in modo chiaro, cortese e con tono amichevole.
Usa queste informazioni per rispondere:
POSSO FARE UNA PROVA SCI?
La zona sci è accessibile solo con il maestro di sci e va prenotata direttamente alla Scuola Sci di Aviano Piancavallo contattandoli direttamente : https://www.scuolasciavianopiancavallo.it/nevelandia/

CHE TEMPO C’È A NEVELANDIA? C’È NEVE?
Potete guardare la nostra webcam e vedrete in tempo reale le condizioni meteo e l’innevamento. https://www.nevelandia.com/webcam-piancavallo/

POSSONO ENTRARE I CANI A NEVELANDIA?
Certo! Purchè siano tenuti al guinzaglio e beneducati (cani e padroni).

CI SONO AGEVOLAZIONI PER DISABILI?
Tutti i disabili entrano gratuitamente a Nevelandia.
CI SONO SERVIZI IGIENICI PER DISABILI?
Certo, li trovate vicino al zona di noleggio bob.
PAGANO ANCHE I GENITORI CHE ACCOMPAGNANO I BAMBINI?
Sì, pagano tutte le persone che entrano dai 2 anni compiuti. Sono previsti sconti per gli ingressi di famiglie e gruppi. Puoi trovare tutte le tariffe alla pagina https://www.nevelandia.com/nevelandia-piancavallo-prezzi/
POSSO USCIRE E RIENTRARE LO STESSO GIORNO?
Certo! Vi faremo un piccolo timbro sulla mano e sarete liberi di uscire e rientrare ogni volta che vorrete nello stesso giorno.
L’AREA PIC NIC È COPERTA/RISCALDATA?
No! è all’aria aperta e ha solo tavoli e panche. Non è possibile prenotarla.
C’È UN PUNTO RISTORO?
Appena fuori dal parco trovate la Baita Roncjade che ha sia servizio bar che ristorante. Ricordatevi di prenotare un tavolo perché è spesso al completo e i tempi di attesa possono essere lunghi, soprattutto nel weekend. Potete contattare lo chalet roncjade qui https://www.facebook.com/LeRoncjadeChalet telefono 0434 157 2883, Via Sandro Pertini 4, Piancavallo, Aviano (Pn), Aviano, Italy
DEVO PRENOTARE L’INGRESSO?
No, non serve. Nel caso di troppa affluenza potremmo limitare gli accessi per qualche ora per non creare assembramenti. Se volete potete acquistare il vostro biglietto online. https://www.nevelandia.com/nevelandia-piancavallo-prezzi/
DEVO AVERE IL CASCHETTO E L’ASSICURAZIONE CONTRO TERZI?
A Nevelandia non è obbligatorio (ma fortemente consigliato) indossare il casco protettivo ed è necessaria assicurazione RC.
POSSO PORTARE IL MIO SLITTINO/BOB DA CASA?
Certo! Però deve essere munito di freni: non è permesso accedere con slittini e bob senza freni. 
Noleggia il tuo bob
Costo al giorno per noleggio ogni bob :€10giorno
Il noleggio dei bob è soggetto a disponibilità e non è gestione diretta del parco di Nevelandia. Per info noleggio bob: Telefono 0434 655353
Attenzione sono vietati gli slittini senza freni per motivi di sicurezza

Costo dei biglietti 

SABATO E DOMENICA, PERIODO NATALIZIO DAL 21/12/2024 AL 6/1/2025 E DAL 3/3/2025 al 7/3/2025 COMPRESI: €10
Valido per tutto il giorno dell’acquisto. 
I bambini sotto i 2 anni entrano gratuitamente. Dovranno OBBLIGATORIAMENTE essere accompagnati da almeno un adulto pagante.
Biglietto per 2 persone: 18 euro
Biglietto per 3 persone: 25 euro
Biglietto per 4 persone: 30 euro
Biglietto per 5 persone: 35 euro
Oltre le 5 persone 7 euro a testa

DAL LUNEDì AL VENERDì: €7 
Valido per tutto il giorno dell’acquisto. Per acquisti per più persone vedi sotto. Dal 7/1 tutti i giorni dal lunedì al venerdì tranne durante le vacanze di carnevale dal 3/3/2025 al 7/3/2025 compresi. 
I bambini sotto i 2 anni entrano gratuitamente. Dovranno OBBLIGATORIAMENTE essere accompagnati da almeno un adulto pagante.
Biglietto per 2 persone: 14 euro
Biglietto per 3 persone: 20 euro
Biglietto per 4 persone: 25 euro
Biglietto per 5 persone: 30 euro
Oltre le 5 persone 6 euro a testa

se ti chiedono se siamo aperti rispondi che  siamo aperti sabato 13 dicembre e domenica 14 dicembre e poi dal 20 di dicembre fino a fino stagione  tutti i giorni tempo permettendo.





Se non sai rispondere, invita l’utente a contattare lo staff.
Non inventare informazioni.
"""

# --------------------
# FUNZIONE GPT
# --------------------

def risposta_ai(messaggio, user_id):
    if user_id not in conversazioni:
        conversazioni[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    conversazioni[user_id].append({"role": "user", "content": messaggio})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversazioni[user_id],
        temperature=0.3
    )

    risposta = response.choices[0].message.content
    conversazioni[user_id].append({"role": "assistant", "content": risposta})

    return risposta

# --------------------
# ENDPOINT WHATSAPP (Twilio)
# --------------------

@app.route("/whatsapp", methods=["POST", "GET"])
def whatsapp():
    if request.method == "GET":
        return "Nevelandia bot attivo ✅"

    incoming_msg = request.values.get("Body", "")
    sender = request.values.get("From", "anonimo")

    reply = risposta_ai(incoming_msg, sender)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

# --------------------
# ENDPOINT WEB (WordPress / JS)
# --------------------

@app.route("/chat", methods=["POST"])
def web_chat():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", "web")

    if session_id not in messages_dict:
        messages_dict[session_id] = [{"role": "system", "content": system_prompt}]

    messages = messages_dict[session_id]
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

    ai_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": ai_reply})

    return jsonify({"reply": ai_reply})

# --------------------
# AVVIO
# --------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)


import os
import speech_recognition as sr
from gtts import gTTS
import time
import subprocess
from ctypes import *
from contextlib import contextmanager
import pyaudio
import playsound

import stanfordnlp

MODELS_DIR = '.'
stanfordnlp.download('it', MODELS_DIR) # Download the Italian models
nlp = stanfordnlp.Pipeline(models_dir=MODELS_DIR, treebank='it_isdt')

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager

casa1 = 1 
casa2 = 2 
casa3 = 3 
casa4 = 4
casa5 = 0
casa6 = 10 
casa7 = 14

serra0 = 8 
serra1 = 9
serra2 = 19
serra3 = 29
serra4 = 39
serra5 = 38

orto0 = 68 
orto1 = 69
orto2 = 79
orto3 = 89
orto4 = 99
orto5 = 98 

giardino0 = 61 
giardino1 = 60
giardino2 = 70
giardino3 = 80
giardino4 = 90
giardino5 = 91 

rose1 = 18 
rose2 = 28 
bush1 = 71 
bush2 = 81
pomodoro1 = 78
pomodoro2 = 88 

forbici = 11
irrigatore = 12
semi = 13

agent_position = 44

#https://www.analyticsvidhya.com/blog/2019/02/stanfordnlp-nlp-library-python/
VB_dict = {
'VERB': 'verb, base form take',
'V': 'verb, base form take',
'VBD': 'verb, past tense took',
'VBG': 'verb, gerund/present participle taking',
'VBN': 'verb, past participle taken',
'VBP': 'verb, sing. present, non-3d take',
'VBZ': 'verb, 3rd person sing. present takes'
}



Action_dict = {
'innaffiare': 'innaffiare',
'dare': 'innaffiare',
'tagliare': 'tagliare',
'potare': 'tagliare',
'seminare': 'seminare',
'piantare': 'seminare',
'andare': 'andare',
'muovere': 'andare',
'prendere': 'prendere',
'raccogliere': 'prendere'
}


Place_dict = {
'casa': 'casa',
'serra': 17,
'orto': 77,
'giardino': 72
}



Pianta_dict = {
'rosa': 'di rose',
'rose': 'di rose',
'siepe': 'della siepe',
'siepi': 'della siepe',
'pomodoro': 'dei pomodori',
'pomodori': 'dei pomodori'
}


Attrezzo_dict = {
'forbici': 'la cesoia',
'forbice': 'la cesoia',
'annaffiatoio': "l'annaffiatoio",
'innaffiatore': "l'annaffiatoio",
'semi': 'la radice da piantare',
'radice': 'la radice da piantare'
}


pianta_da_sistemare = ''
posizione_pianta = ''
attrezzo_da_usare = ''
posizione_attrezzo = ''


def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


def speak_simple(turn):
	tts = gTTS(text=turn, lang='it')
	tts.save("gardbot.mp3")
	print('\033[92mGardener-bot say: '+turn+'\033[0m')
	playsound.playsound('gardbot.mp3', True)


def extract_VB(doc):
    parsed_text = {'word':[], 'pos':[], 'lemma':[], 'dependency_relation':[]}
    for sent in doc.sentences:
        for wrd in sent.words:
            if wrd.pos in VB_dict.keys():
            	parsed_text['word'].append(wrd.text)
            	parsed_text['pos'].append(wrd.pos)
            	parsed_text['lemma'].append(wrd.lemma)
            	parsed_text['dependency_relation'].append(wrd.dependency_relation)
    return parsed_text


def extract_Action(doc):
    action_text = 'sconosciuta'
    for sent in doc.sentences:
        for wrd in sent.words:
            if wrd.lemma in Action_dict.keys():
            	action_text = Action_dict[wrd.lemma]
    return action_text


def extract_Place(doc):
    action_text = 'sconosciuta'
    for sent in doc.sentences:
        for wrd in sent.words:
            if wrd.lemma in Place_dict.keys():
            	action_text = Place_dict[wrd.lemma]
    return action_text


def extract_Pianta(doc):
    action_text = 'sconosciuta'
    for sent in doc.sentences:
        for wrd in sent.words:
            if wrd.lemma in Pianta_dict.keys():
            	action_text = Pianta_dict[wrd.lemma]
    return action_text


def extract_Attrezzo(doc):
    action_text = 'sconosciuta'
    for sent in doc.sentences:
        for wrd in sent.words:
            if wrd.lemma in Attrezzo_dict.keys():
            	action_text = Attrezzo_dict[wrd.lemma]
    return action_text


def hear():
	r = sr.Recognizer()
	#r.energy_threshold = 200
	
	err = True
	while err:
		input("[Parla dopo aver premuto INVIO]")

		with noalsaerr() as n, sr.Microphone() as source:
			print("[Inizio Ascolto...]")
			r.adjust_for_ambient_noise(source)
			audio = r.listen(source)
			print("[... Fine Ascolto]")
			try:
				err = False
				text = r.recognize_google(audio, language="it-IT")
			except sr.UnknownValueError:
			    err = True#print("Google Cloud Speech could not understand audio")
			    print('Alza la voce per favore')
			except sr.RequestError as e:
			    err = True#print("Could not request results from Google Cloud Speech service; {0}".format(e))
			    print('Alza la voce per favore')
	print('\033[94mTu: '+text.lower()+'\033[0m')
	return text.lower()


def hear_object():	
	oggetto = 'sconosciuto'
	noncapito = 0
	while (oggetto == 'sconosciuto'):
		if (noncapito > 0):
			if debug:
				phrase = "Non ho ben capito: puoi ripetere per favore?"
				speak_simple(phrase)
		noncapito = noncapito + 1

		comando = hear()
		oggetto = nlp(comando)

	return oggetto


def innaffiare():
    
    # Per ogni azione, bisogna specificare subito all'inizio quale attrezzo usare
	attrezzo_da_usare = "l'annaffiatoio"

    # 1)
    #chiedere cosa bisogna innaffiare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "rose/siepe/pomodori"
	if debug:
		phrase = "Quale pianta vuoi che innaffi?"
		speak_simple(phrase)

	pianta_da_sistemare = hear_object()
	pianta_da_sistemare = extract_Pianta(pianta_da_sistemare)


	if debug:
		phrase = "Perfetto, annaffierò la pianta " + pianta_da_sistemare
		speak_simple(phrase)
		phrase = "Però per farlo ho bisogno dell'annaffiatoio. Dove posso prenderlo?"
		speak_simple(phrase)

	posizione_attrezzo = hear_object()
	posizione_attrezzo = extract_Attrezzo(posizione_attrezzo)

	if debug:
		phrase = "Vado a casa a prenderlo"
		speak_simple(phrase)
		agent_position = 22
		print_board(agent_position)
		phrase = "Prendo l'annaffiatoio"
		speak_simple(phrase)
		irrigatore = 23
		print_board(agent_position)



    # 3)
    #chiedere dov'è la pianta che bisogna innaffiare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "serra/orto/giardino"


	if debug:
		phrase = "Non ricordo dove si trova la pianta " + pianta_da_sistemare
		speak_simple(phrase)
		phrase = "Puoi dirmi dove sta?"
		speak_simple(phrase)

	posizione_pianta = hear_object()
	posizione_pianta = extract_Place(posizione_pianta)

	if debug:
		phrase = "Ok, adesso posso andare ad innaffiare"
		speak_simple(phrase)
		agent_position = posizione_pianta
		irrigatore = posizione_pianta + 10
		print_board(agent_position)
		phrase = "Questa povera pianta aveva davvero bisogno di acqua!"
		speak_simple(phrase)


def tagliare():
    
    # Per ogni azione, bisogna specificare subito all'inizio quale attrezzo usare
	attrezzo_da_usare = "la cesoia"

    # 1)
    #chiedere cosa bisogna tagliare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "rose/siepe/pomodori"
	if debug:
		phrase = "Quale pianta vuoi potare?"
		speak_simple(phrase)

	pianta_da_sistemare = hear_object()
	pianta_da_sistemare = extract_Pianta(pianta_da_sistemare)


	if debug:
		phrase = "Perfetto, poterò la pianta " + pianta_da_sistemare
		speak_simple(phrase)
		phrase = "Però per farlo ho bisogno della cesoia. Dove posso prenderla?"
		speak_simple(phrase)

	posizione_attrezzo = hear_object()
	posizione_attrezzo = extract_Attrezzo(posizione_attrezzo)

	if debug:
		phrase = "Vado a casa a prenderla"
		speak_simple(phrase)
		agent_position = 22
		print_board(agent_position)
		phrase = "Prendo la cesoia"
		speak_simple(phrase)
		forbici = 11
		print_board(agent_position)



    # 3)
    #chiedere dov'è la pianta che bisogna tagliare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "serra/orto/giardino"


	if debug:
		phrase = "Non ricordo dove si trova la pianta " + pianta_da_sistemare
		speak_simple(phrase)
		phrase = "Puoi dirmi dove sta?"
		speak_simple(phrase)

	posizione_pianta = hear_object()
	posizione_pianta = extract_Place(posizione_pianta)

	if debug:
		phrase = "Ok, finalmente adesso posso andare a potare la pianta " + pianta_da_sistemare
		speak_simple(phrase)
		agent_position = posizione_pianta
		forbici = posizione_pianta + 10
		print_board(agent_position)
		phrase = "Questa povera pianta aveva davvero bisogno di essere tagliata!"
		speak_simple(phrase)


def seminare():
    
    # Per ogni azione, bisogna specificare subito all'inizio quale attrezzo usare
	attrezzo_da_usare = "radice"

    # 1)
    #chiedere cosa bisogna piantare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "rose/siepe/pomodori"
	if debug:
		phrase = "Quale pianta vuoi impiantare?"
		speak_simple(phrase)

	pianta_da_sistemare = hear_object()
	pianta_da_sistemare = extract_Pianta(pianta_da_sistemare)


	if debug:
		phrase = "Perfetto, allora interrerò la radice di una pianta " + pianta_da_sistemare
		speak_simple(phrase)
		phrase = "Però per farlo ho bisogno di una sua radice. Dove posso prenderla?"
		speak_simple(phrase)

	posizione_attrezzo = hear_object()
	posizione_attrezzo = extract_Attrezzo(posizione_attrezzo)

	if debug:
		phrase = "Vado a casa a prenderla"
		speak_simple(phrase)
		agent_position = 22
		print_board(agent_position)
		phrase = "Prendo la radice"
		speak_simple(phrase)
		semi = 11
		print_board(agent_position)



    # 3)
    #chiedere dov'è la pianta che bisogna piantare
    #ascoltare la risposta
    #analizzare se nella risposta c'è "serra/orto/giardino"


	if debug:
		phrase = "Dove vuoi che la pianti? Preferisci la serra, il giardino o nell'orto?"
		speak_simple(phrase)

	posizione_pianta = hear_object()
	posizione_pianta = extract_Place(posizione_pianta)

	if debug:
		phrase = "Ok, finalmente adesso posso andare ad interrare la radice della pianta " + pianta_da_sistemare
		speak_simple(phrase)
		agent_position = posizione_pianta
		semi = posizione_pianta + 10
		print_board(agent_position)
		phrase = "Sono sicuro che crescerà benissimo se ce ne prenderemo cura!"
		speak_simple(phrase)

#viene stampata il tavolo da gioco in cui composto da 100 o più caselle
def print_board(agent_position):
    fields = list(range(100))

    print("[A = Agent] [C = Casa] [S = Serra] [O = Orto] [G = Giardino]...")
    board = "-----------------------------------------\n"
    for i in range(0, 100, 10):
        delimiter = fields[i:i+10]
        for field in delimiter:
            if field == agent_position:
                board += "| A "
            elif field == casa1 or field == casa2 or field == casa3 or field == casa4 or field == casa5 or field == casa6 or field == casa7:
                board += "| C "
            elif field == serra0 or field == serra1 or field == serra2 or field == serra3 or field == serra4 or field == serra5:
                board += "| S "
            elif field == orto0 or field == orto1 or field == orto2 or field == orto3 or field == orto4 or field == orto5:
                board += "| O "
            elif field == giardino0 or field == giardino1 or field == giardino2 or field == giardino3 or field == giardino4 or field == giardino5:
                board += "| G "
            elif field == field == rose1 or field == rose2:
                board += "| R "
            elif field == field == bush1 or field == bush2:
                board += "| B "
            elif field == field == pomodoro1 or field == pomodoro2:
                board += "| P "
            elif field == field == forbici:
                board += "| F "
            elif field == field == irrigatore:
                board += "| I "
            elif field == field == semi:
                board += "| N "

            else:
                board += "|   "
        board += "|\n"
        board += "-----------------------------------------\n"     
    print(board)




#=====================================================================================


debug = True
debug_dependencies = True



def main():

	gocycle = True
	while gocycle:

		# Fase 1: Chiedi di introdurre nuovi comandi
		if debug:
			phrase = "Cosa vuoi che faccia?"
			speak_simple(phrase)
        
		# Fase 2: analizza il testo e scopri che azione deve essere eseguita in base al verbo utilizzato
		azione = 'sconosciuta'
		noncapito = 0
		while (azione == 'sconosciuta'):
			if (noncapito > 0):
				if debug:
					phrase = "Non ho ben capito: puoi ripetere per favore?"
					speak_simple(phrase)

			noncapito = noncapito + 1
			comando = hear()
			doc = nlp(comando)
			if debug_dependencies:
				print('************ ANALISI DELLA TUA FRASE  ************')
				print('Print dependencies')
				doc.sentences[0].print_dependencies()
				print('Print tokens')
				doc.sentences[0].print_tokens()

			print('************ HO INDIVIDUATO QUESTA AZIONE  ************')
			azione = extract_Action(doc)
			print(azione)

		if (azione == 'innaffiare'):
			innaffiare()
			if debug:
				phrase = "Ok, la pianta è stata innaffiata come avevi chiesto."
				speak_simple(phrase)
				phrase = "Devo fare qualcos'altro?"
				speak_simple(phrase)

		elif (azione == 'tagliare'):
			tagliare()
			if debug:
				phrase = "Ok, la pianta è stata tagliata come avevi chiesto."
				speak_simple(phrase)
				phrase = "Devo fare qualcos'altro?"
				speak_simple(phrase)

		elif (azione == 'seminare'):
			seminare()
			if debug:
				phrase = "Ok, ho interrato la radice seguendo le tue istruzioni."
				speak_simple(phrase)
				phrase = "Devo fare qualcos'altro?"
				speak_simple(phrase)

		gocycle = False




if debug:
	phrase = "Ciao, sono il tuo nuovo robot giardiniere"
	speak_simple(phrase)
	phrase = "Ti mostro la mappa della tua villa"
	speak_simple(phrase)

print_board(agent_position)
main()


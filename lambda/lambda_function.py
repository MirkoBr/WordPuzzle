# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import random
import logging
import ask_sdk_core.utils as ask_utils

# packages and functions to display stuff on devices with screens
import json
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

# DynamoDbAdapter
import os
import boto3
#from ask_sdk.standard import StandardSkillBuilder
#from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')

ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)


# interceptors
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.dispatch_components import AbstractResponseInterceptor

# simple card
#from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
#from ask_sdk_core.handler_input import HandlerInput
#from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

# builder
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


LANGUAGES = {
    "en-US": {
        "GAME_NAME": "Word Puzzle",
        "WELCOME": "Welcome to 'Word Puzzel'. ", 
        "INFO": "I'll give you a random word, and you have to think of another word that matches it. The more letters and positions that match, the better. ",
        "TIP": "One quick tip before we get started. This game is easier on devices with screens. But if you don't have one, you can also use pen and paper to write something down in between. ",
        "PLAYER_START": [
            "Should I start a new round or take an example?",
            "We can jump right into a new round, or I can give you an example first. What would you like?",
            "Shall I start a new round or give you an example?",
            "Would you like an example, or should I start a new round?"
            ],
        "RESPONSE": "I said: ",
        "EXAMPLE_TEXT": "Okay, here's an example. For example, if I say the word %s, then %s would be a good answer. You would get %s points for it. ",
        "EXAMPLE_INFO": "The more letters you put in the right position, the more points you get. <break time='0.5s'/>",
        "EXAMPLE_TIP": "It's sometimes easier to play on divices with screens. But if you don't have one you can use pen and paper to write things down in between.",
        "NEW_SENTENCE_PRE": ["Okay. ", "Alright. "],
        "FIRST_ROUND": "Starting a new round. ",
        "NEW_SENTENCE_FIRST_OPTIONS": [
            "The first word is: ", "Your first word is: ", "Round one starts with: ",
            "We start with: ", "Try this one: "
            ],
        "NEW_SENTENCE_MIDDLE_OPTIONS": [
            "Your next word is: ", "The next word is: ", "The next word for you is: ",
            "We continue with this word: "
            ],
        "NEW_SENTENCE_LAST_OPTIONS": [
            "On to the last word in this round. It is: ", "The last word for this round is: ",
            "We finish off the round with this word: ", "The last word I have for you in this round is: "
            ],
        "ANSWER": ["What's your answer? ", "What is your answer? ", "What's your word? "],
        "ANSWER_ONGOING": ["The word is: ", "You already have a word, it is: ", "The word is: "],
        "PROMPT_TO_EXAMPLE": "Or do you need an example? ",
        "PROMPT_TO_ANSWER": "What is your answer?",
        "PROMPT_TO_ANSWER_CHANGE": "Ok. What is your new answer?",
        "CURRENT_SENTENCE_CARD_TITLE": "Current word is: ",
        "REPEAT_ANSWER": ["I understood: ", "You said: ", "Your answer is: ", "Let me repeat: "],
        "GET_ANSWER_LOGGED": [
            "Did I understand that correctly? ",
            "Is that right? ",
            "Correct? ", "Right? ",
            "Are you sure about that? ",
            "Should I log that in? ",
            "Do you want me to log it in? "
            ],
        "GET_ANSWER_LOGGED_REPEAT": "Say 'Yes' to log in the answer or say 'No' to change it.  ",
        "RESULT_SCORE_BAD": [
            "Too bad, you only got %s of %s points. ",
            "Oh dear, only %s of %s points. ",
            "Oops, only %s of %s points. Let's forget about that. ",
            "Oops, %s of %s points. We should forget about that quickly. ",
            "You only scored %s of %s points. Just keep trying. ",
            "Phew, someone's a little talentless there. %s of %s points. "
        ],
        "RESULT_SCORE_MEDIUM": [
            "Good performance. You scored %s out of %s points. ",
            "Nice try. You got %s out of %s points. ",
            "Not the worst. You got %s out of %s points. ",
            "You got %s out of %s points this time. ",
            "Alright. %s out of %s points is decent. "
        ],
        "RESULT_SCORE_GREAT": [
            "Wow! You got %s out of %s points. That's amazing! ",
            "Nice job! You got %s out of %s points. ", 
            "Well played! You got %s out of %s points. ", 
            "You rock! You got %s out of %s points. ",
            "Nice one! You got %s out of %s points. ",
            "Holy moly! You got %s out of %s points. ", 
            "Wow! You got %s out of %s points. That's really good! ", 
            "OMG! You got %s out of %s points. You are crushing it! ",
            "OMG! You got %s out of %s points. You are awesome! ",
        ],
        "ANSWER_NOT_UNDERSTOOD": "It seems that I did not fully understand your answer. Can you repeat it for me?",
        "ROUND_FINISH_FIRST_HIGHSCORE": f"<amazon:emotion name='excited' intensity='high'> Yeah! You completed your very first round with a total of %s out of %s possible points. </amazon:emotion>",
        "ROUND_FINISH_LOG_FIRST_HIGHSCORE": "I will remember this as your current high score. ",
        "ROUND_FINISH_PROMPT_NEW_ROUND_FIRST_HIGHSCORE": "You can start a new round and try to beat the high score, or quit the game. " ,
        "FIRST_HIGHSCORE_CARD_TITLE": "First highscore!!!",
        "POINTS_CARD_TEXT": f"You finished the round with: %s out of %s possible points",
        "ROUND_FINISH_NEW_HIGHSCORE": f"<amazon:emotion name='excited' intensity='high'> Nice one!!! </amazon:emotion> <amazon:emotion name='excited' intensity='medium'> You finished with a new highscore. </amazon:emotion>",
        "ROUND_FINISH_LOG_NEW_HIGHSCORE": f"Your old highscore was %s and the new one is %s points. ",
        "ROUND_FINISH_PROMPT_NEW_ROUND_NEW_HIGHSCORE": "You can start a new round and try to improove your highscore right away. You could also check out your game stats or exit the game. ",
        "NEW_HIGHSCORE_CARD_TITLE": "New highscore!!!",
        "ROUND_FINISH_NO_HIGHSCORE": f"<amazon:emotion name='disappointed' intensity='low'>GG Well played. </amazon:emotion> You finished the round with %s out of %s possible points. " ,
        "ROUND_FINISH_CLOSE_TO_HIGHSCORE": f"<amazon:emotion name='excited' intensity='low'> That was really close to your highscore of %s. </amazon:emotion> Say 'start a new round' to play another round and try to beat your highscore right away. ",
        "ROUND_FINISH_FAR_FROM_HIGHSCORE": f"Your current highscore is %s, that's much better. Say 'start a new round' to play another round and try to beat your highscore right away. ",
        "NO_HIGHSCORE_CARD_TITLE": "End of round",
        "STATS_SUMMARY": f"Here are your game statistics: You have played %s games with %s rounds. In total you scored %s points with a highscore of %s.",
        "HELP_IN_ROUND": "Say 'my answer is:' followed by your answer. You can say 'next:' to continue. ",
        "HELP_NO_ROUND": "You did not start a new round yet. You can say 'new round' to start a new round, ask me for your game statistics or exit the game. ",
        "STOP": "Okay. I stopped. What do you want to do next? You can say help or exit.",
        "FALLBACK": "Shit. Something went wrong. Please restart the skill. ",
        "END": [
            "Take care. ", "Bye! ", " See you. ", 
            "Take care. If you liked the game then feel free to give us a review in the Alexa App. ", 
            "Bye! If you liked the game then feel free to give us a review in the Alexa App. ", 
            "See you. If you liked the game then feel free to give us a review in the Alexa App. ",
            ],
        "INTENT_REFLECT": f"You just triggered %s",
        "EXCEPTION": "I think my mainboard is burned out. Please restart the skill. ",
        "ACTION": "What do you want to do? ",
        "ANSWER_SENTENCE_CARD_TITLE": "Your word is: ",
        "PROMPT_TO_CONTINUE": "You can ask me for your personal statistics, or exit the game. " ,
        "DISPLAY_PROMPT_TO_START_ROUND": "Try 'new round' to start a new round. ",
        "DISPLAY_PROMPT_TO_ANSWER": "Try 'my answer is:' ",
        "DISPLAY_CURRENT_WORD_HEADER": "The current word is: ",
        "DISPLAY_CURRENT_ANSWER_HEADER": "Your answer is: ",
        "DISPLAY_CURRENT_ROUND_COUNTER": f"Word %s/5",
        "DISPLAY_ALL_TIME_ROUND_COUNTER": f"Round %s",
        "DISPLAY_PROMPT_TO_LOGGIN": "Try 'Yes' or 'No'",
        "DISPLAY_CURRNET_SCORE": f"%s / %s Points",
        "DISPLAY_CURRENT_ROUND_CHECK": "The evaluation of your answer is:",
        "ASK_NEXT_WORD": "Say 'next' to continue. ",
        "DISPLAY_PROMPT_NEXT_WORD": "Try 'next' ",
        "DISPLAY_ROUND_END": "End of round",
        "DISPLAY_POINT_NAME": "Points",
        "DISPLAY_END_MESSAGE": ["!!! New highscore !!!", "Close to highscore", "No highscore"],
        "DISPLAY_ROUND_END_SCORE": f"%s out of %s points",
        "DISPLAY_PROMPT_TO_CONTINUE": "Try 'continue'.",
        "DISPLAY_CURRENT_SCORE_DETAILS": "Points-plus: %s, Points-penalty %s, Points-final: %s",
        "EXAMPLE_COUNTER": "Example",
        "EXAMPLE_WORD": "Snowman",
        "EXAMPLE_ANSWER": "Snowball",
        "EXAMPLE_DISPLAY_CURRENT_ROUND_CHECK": "This is how the example check looks like:",
        "EXAMPLE_SCORE_EXPLANATION": "For the answer '%s' for word '%s' is worth %s points.",
        "STATS_TITLE_HEADER": "Stats",
        "STATS_TITLE": "Personal statistics",
        "STATS_FEATURES_GAMES_PLAYED": f"Games played: %s",
        "STATS_FEATURES_ROUNDS_PLAYED": f"Rounds played: %s",
        "STATS_FEATURES_POINT_SCORE": f"Points scored: %s",
        "STATS_FEATURE_HIGHSCORE": f"Highscore: %s",
        "BASH_USER": "Haha. You can't fool me! You get Zero points for this. "
    },
    "de-DE": {
        "GAME_NAME": "Wörter-Puzzel",
        "WELCOME": "Willkommen zu 'Wörter Puzzel'. ",
        "INFO": "Ich werde dir ein zufälliges Wort sagen, zu dem du dir ein passendes anderes Wort ausdenken musst. Je mehr Buchstaben und Positionen übereinstimmen, umso besser. ",
        "TIP": "Ein letzer Hinweis bevor wir anfangen. Es kann einfacher sein an einem Gerät mit Bildschirm zu spielen, oder Stift und Papier bereit zu halten. ",
        "PLAYER_START" : [
            "Soll ich eine neue Runde für dich starten oder möchtest du zuerst ein Beispiel hören? ",
            "Wir können direkt in eine neue Runde starten oder uns zuerst ein Beispiel anhören. Was willst du tun? ",
            "Sollen wir eine neue Runde starten oder willst du ein Beispiel hören? ", 
            "Sollen wir uns erstmal ein Beispiel anschauen, oder willst du direkt eine neue Runde starten? "
            ],
        "RESPONSE": "Ich sagte: ",
        "EXAMPLE_TEXT": "Okay, hier ist ein Beispiel. Sage ich zum Beispiel das Wort %s, dann wäre %s eine gute Antwort. Du würdest dafür %s Punkte bekommen. ",
        "EXAMPLE_INFO": "Je mehr Buchstaben du an die richtige Position bekommst, desto mehr Punkte gibt es. <break time='0.5s'/>",
        "EXAMPLE_TIP": "Es kann einfacher sein an einem Gerät mit Bildschirm zu spielen, oder Stift und Papier bereit zu halten.",
        "NEW_SENTENCE_PRE": ["OK. ", "Alles klar. ", "Okay. "],
        "FIRST_ROUND": "Eine neue Runde beginnt. ",
        "NEW_SENTENCE_FIRST_OPTIONS": [
            "Das erste Wort ist: ", "Dein erstes Wort ist: ", "Runde eins beginnt mit diesem Wort: ",
            "Wir fangen mit diesem Wort an: ", "Mein erstes Wort ist: "
            ],
        "NEW_SENTENCE_MIDDLE_OPTIONS": [
            "Dein nächstes Wort ist: ", "Das nächste Wort ist: ", "Das nächste Wort für dich ist: ",
            "Es geht mit diesem Wort weiter: " , "Lass uns mit diesem Wort weiter machen: " 
            ],
        "NEW_SENTENCE_LAST_OPTIONS": [
            "Das letzte Wort für diese Runde ist: ", "Wir beenden die Runde mit diesem Wort: ",
            "Zum Abschluss der Runde habe ich noch dieses Wort für dich: ", "Das letzte Wort das ich diese Runde für dich habe ist: ",
            "Das letzte Wort in dieser Runde lautet: "
            ],
        "ANSWER": ["Was ist deine Antwort? ", "Wie lautet deine Antwort? ", "Wie lautet dein Wort? "],
        "ANSWER_ONGOING": ["Das Wort war: ", "Ich hatte dir schon ein Wort genannt. Es lautet: ", "Mein Wort für dich war: "],
        "PROMPT_TO_EXAMPLE": "Oder brauchst du eine Beispiel? ",
        "PROMPT_TO_ANSWER": "Wie lautet deine Antwort ?",
        "PROMPT_TO_ANSWER_CHANGE": "Alles klar. Wie lautet deine neue Antwort? ",
        "CURRENT_SENTENCE_CARD_TITLE": "Das aktuelle Wort lautet: ",
        "REPEAT_ANSWER": ["Ich habe folgendes verstanden: ", "Du hast gesagt: ", "Deine Antwort war: ", "Lass mich deine Antwort wiederholen, sie lautet: "],
        "GET_ANSWER_LOGGED": [
            "Habe ich das richtig verstanden? ",
            "Ist das richtig? ",
            "Ist das deine Antwort? ",
            "Bist du dir mit dieser Antwort sicher? ",
            "Soll ich diese Antwort wirklich einloggen? "
            ],
        "GET_ANSWER_LOGGED_REPEAT": "Sage 'Ja' um deine Antwort ein zu loggen, oder sage 'Nein' um sie zu ändern. ",
        "RESULT_SCORE_BAD": [
            f"Schade, du hast nur %s von %s möglichen Punkten geschafft. ",
            f"Oh nein, nur %s von %s möglichen Punkten. ",
            f"Ups, nur %s von %s möglichen Punkten. Beim nächsten mal wird es sicher besser. ",
            f"Ups, nur %s von %s möglichen Punkten. Da ist noch Luft nach oben. ",
            f"Hmm nur %s von %s möglichen Punkten. Versuch es einfach weiter. "
        ],
        "RESULT_SCORE_MEDIUM": [
            f"Guter Versuch. Du hast %s von %s möglichen Punkten geschafft. ",
            f"Ok. Das waren %s von %s möglichen Punkten. ",
            f"Gar nicht so schlecht. Das waren %s von %s möglichen Punkten. ",
            f"Ok. Dieses mal waren es %s von %s möglichen Punkten. ",
            f"Ok. %s von %s möglichen Punkten sind ganz anständig. "
        ],
        "RESULT_SCORE_GREAT": [
            f"WOW! Du hast %s von %s möglichen Punkten geschafft. Genial! ",
            f"Gute Arbeit! Das waren %s von %s möglichen Punkten. ", 
            f"Gut gespielt! Das waren %s von %s möglichen Punkten. ", 
            f"Der Knaller! Du hast %s von %s möglichen Punkten geschafft. ",
            f"WOW! Mit %s von %s möglichen Punkten hätte ich von dir nicht gerechnet. ",
            f"Ehhh Bitte was? Das waren %s von %s möglichen Punkten. Voll Gut! ", 
            f"Ok. Mit %s von %s möglichen Punkten hast du wohl auch dich selbst überrascht. Echt gut! ", 
            f"Du bist der Hammer! Das waren %s von %s möglichen Punkten. "
        ],
        "ANSWER_NOT_UNDERSTOOD": "Ich glaube ich habe deine Antwort nicht ganz verstanden. Kannst du sie für mich noch einmal wiederholen?",
        "ROUND_FINISH_FIRST_HIGHSCORE": f"<amazon:emotion name='excited' intensity='high'> Yeah Yeah. Du hast deine aller erste Runde mit %s von %s möglichen Punkten beendet. </amazon:emotion>",
        "ROUND_FINISH_LOG_FIRST_HIGHSCORE": "Ich merke mir die Punktzahl als deinen aktuellen Highscore. ",
        "ROUND_FINISH_PROMPT_NEW_ROUND_FIRST_HIGHSCORE": "Du kannst eine neue Runde starten um direkt zu versuchen deinen Highscore zu schlagen, oder das Spiel beenden. " ,
        "FIRST_HIGHSCORE_CARD_TITLE": "Aller erster Highscore!!!",
        "POINTS_CARD_TEXT": f"Du beendest die Runde mit: %s von %s möglichen Punkten",
        "ROUND_FINISH_NEW_HIGHSCORE": f"<amazon:emotion name='excited' intensity='high'> Gut gemacht!!! </amazon:emotion> <amazon:emotion name='excited' intensity='medium'> Du beendest die Runde mit einem neuen Highscore. </amazon:emotion>",
        "ROUND_FINISH_LOG_NEW_HIGHSCORE": f"Dein alter Highscore lag bei %s Punkten und dein neuer ist besser, mit %s Punkten. ",
        "ROUND_FINISH_PROMPT_NEW_ROUND_NEW_HIGHSCORE": "Du kannst eine neue Runde starten um direkt zu versuchen deinen Highscore zu schlagen, deine Spiel Statistiken anschauen, oder das Spiel beenden. ",
        "NEW_HIGHSCORE_CARD_TITLE": "Neuer Highscore!!!",
        "ROUND_FINISH_NO_HIGHSCORE": f"<amazon:emotion name='disappointed' intensity='low'> Gut gespielt. </amazon:emotion> Du beendest die Runde mit %s von %s möglichen Punkten. " ,
        "ROUND_FINISH_CLOSE_TO_HIGHSCORE": f"<amazon:emotion name='excited' intensity='low'> Das war wirklich knapp unter deinem Highscore von %s Punkten. </amazon:emotion> Sage 'starte eine neue Runde' und versuche dich direkt zu verbessern. ",
        "ROUND_FINISH_FAR_FROM_HIGHSCORE": f"Dein aktueller Highscore ist mit %s Punkten viel besser. Sage 'starte eine neue Runde' und versuche dich direkt zu verbessern. ",
        "NO_HIGHSCORE_CARD_TITLE": "Ende der Runde. ",
        "STATS_SUMMARY": f"Hier sind deine Spiel Statistiken: Du hast %s Spiele mit %s Runden gespielt. Insgesamt kommst du dabei auf %s Punkte mit einem Highscore von %s. ",
        "HELP_IN_ROUND": "Sage 'Meine Antwort ist:' gefolgt von deinem Wort, oder sage 'weiter' um fortzufahren. ",
        "HELP_NO_ROUND": "Du hast noch keine neue Runde angefangen. Sage 'Starte eine neue Runde' um eine neue Runde zu starten. Du kannst mich auch nach deinen Spiel Statistiken fragen, oder das Spiel beenden. ",
        "STOP": "Ok. Abgebrochen. Was möchtest du als nächstes machen? Du kannst Hilfe oder Beenden sagen. ",
        "FALLBACK": "Scheiße. Irgendwas stimmt gar nicht. Bitte starte den Skill erneut. ",
        "END": [
            "Machs gut.", "Auf wiedersehen. ", " Tschüss! ", 
            "Machs gut. Wenn dir das Spiel gefallen hat dann gib uns gerne eine Bewertung in der Alexa App. ", 
            "Auf wiedersehen.  Wenn dir das Spiel gefallen hat dann gib uns gerne eine Bewertung in der Alexa App.", 
            "Tschüss!  Wenn dir das Spiel gefallen hat dann gib uns gerne eine Bewertung in der Alexa App. ",
            ],
        "INTENT_REFLECT": f"Du hast %s ausgelöst. ",
        "EXCEPTION": "Ich glaube meine Platine ist durchgeschmort. Bitte starte den Skill erneut. ",
        "ACTION": "Was möchtest du machen? ",
        "ANSWER_SENTENCE_CARD_TITLE": "Dein Satz lautet: ",
        "PROMPT_TO_CONTINUE": "Frage mich zum Beispiel nach deinen persönlichen Statistiken, oder beende das Spiel. ",
        "DISPLAY_PROMPT_TO_START_ROUND": "Versuche 'neue Runde' um eine neue Runde zu starten. ",
        "DISPLAY_PROMPT_TO_ANSWER": "Versuche 'meine Antwort ist:' ",
        "DISPLAY_CURRENT_WORD_HEADER": "Das aktuelle Wort ist: ",
        "DISPLAY_CURRENT_ANSWER_HEADER": "Deine Antwort ist: ",
        "DISPLAY_CURRENT_ROUND_COUNTER": f"Wort %s/5",
        "DISPLAY_ALL_TIME_ROUND_COUNTER": f"Runde %s",
        "DISPLAY_PROMPT_TO_LOGGIN": "Versuche es mit 'Ja' oder 'Nein'",
        "DISPLAY_CURRNET_SCORE": f"%s / %s Punkten",
        "DISPLAY_CURRENT_ROUND_CHECK": "Deine Auswertung deiner Antwort ist:",
        "ASK_NEXT_WORD": "Sage 'weiter' um fortzufahren. ",
        "DISPLAY_PROMPT_NEXT_WORD": "Versuche es mit 'weiter' ",
        "DISPLAY_ROUND_END": "Ende der Runde",
        "DISPLAY_POINT_NAME": "Punkte",
        "DISPLAY_END_MESSAGE": ["!!! Neuer Highscore !!!", "Knapp kein Highscore", "Leider kein Highscore"],
        "DISPLAY_ROUND_END_SCORE": f"%s von %s Punkten",
        "DISPLAY_PROMPT_TO_CONTINUE": "Versuche es mit 'weiter'.",
        "DISPLAY_CURRENT_SCORE_DETAILS": "Plus-Punkte: %s, Straf-Punkte: %s, Gesamt-Punkte: %s",
        "EXAMPLE_COUNTER": "Beispiel",
        "EXAMPLE_WORD": "Schneemann",
        "EXAMPLE_ANSWER": "Schneeball",
        "EXAMPLE_DISPLAY_CURRENT_ROUND_CHECK": "Die Beispielauswertung sieht so aus:",
        "EXAMPLE_SCORE_EXPLANATION": f"Für die Antwort '%s' zum Wort '%s' hättest du %s Punkte bekommen.",
        "STATS_TITLE_HEADER": "Stats",
        "STATS_TITLE": "Persönliche Statistiken",
        "STATS_FEATURES_GAMES_PLAYED": f"Spiele gestartet: %s",
        "STATS_FEATURES_ROUNDS_PLAYED": f"Runden gespielt: %s",
        "STATS_FEATURES_POINT_SCORE": f"Punkte bekommen: %s",
        "STATS_FEATURE_HIGHSCORE": f"Highscore: %s",
        "BASH_USER": "Haha. Mich kannst du nicht verarschen! Dafür gibt es Null Punkte. "
    }
}


def get_language(locale):
    return LANGUAGES[locale]


def get_player_start(locale):
    questions = get_language(locale)['PLAYER_START']
    return random.choice(questions)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):

        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        
        if session_attributes['visits'] == 0:
            # new user
            speak_output = f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_tally_positive_01'/>" + \
                get_language(locale)['WELCOME'] + \
                get_language(locale)['INFO'] + \
                f"<break time='0.5s'/> " + \
                get_player_start(locale) 
            ask_output = get_language(locale)['ACTION'] + \
                get_language(locale)['TIP'] 
        else:
            # returning user
            speak_output = f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_tally_positive_01'/>" + \
                get_language(locale)['WELCOME'] + \
                f"<break time='0.5s'/> " + \
                get_player_start(locale) 
            ask_output = get_language(locale)['ACTION'] + \
                get_language(locale)['TIP'] 
        
        session_attributes['response'] = get_language(locale)['RESPONSE']
        session_attributes['visits'] = session_attributes['visits'] + 1
        handler_input.attributes_manager.session_attributes = session_attributes
        
        #====================================================================
        # Visual components
        #====================================================================
        
        
        with open ("./documents/apl_homescreen.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "start": get_language(locale)['GAME_NAME'],
                                "help": get_language(locale)['DISPLAY_PROMPT_TO_START_ROUND']
                            },
                            "assets" : {
                                "logo": utils.create_presigned_url('Media/logo_new.png'),
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


class GetExampleIntentHandler(AbstractRequestHandler):
    """Explain the game in more detail"""
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("GetExampleIntent")(handler_input)
            )
    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        #session_attributes['change_answer_possible'] = 0
        #session_attributes['logg_answer_possible'] = 0
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        # make example answer check
        import sentenceFunctions
        example_word = get_language(locale)['EXAMPLE_WORD']
        example_answer = get_language(locale)['EXAMPLE_ANSWER']
        example_result = sentenceFunctions.check_answer(example_word, example_answer)
        
        example_points = example_result[1]
        example_points_max = example_result[0]
        example_alignment_original = example_result[2]
        example_alignment_answer = example_result[3]
        example_penalty_score = example_result[4]
        example_answer_score = example_result[5]
        
        # prep result
        speak_output = f"{get_language(locale)['EXAMPLE_TEXT'] % (example_word, example_answer, example_points)}" + \
            get_language(locale)['EXAMPLE_INFO'] + \
            get_language(locale)['EXAMPLE_TIP'] 
        ask_output = get_language(locale)['ACTION']
        
        #card_title = get_language(locale)['EXAMPLE_CARD_TITLE']
        #card_text = get_language(locale)['EXAMPLE_CARD_TEXT']
        
        if session_attributes['in_round'] == False:
            session_attributes['response'] = get_language(locale)['RESPONSE'] + \
                get_language(locale)['EXAMPLE_TEXT'] + \
                get_language(locale)['EXAMPLE_INFO']
        
        if session_attributes['in_round'] == True:
            current_sentence = session_attributes['current_sentence']
            session_attributes['response'] = get_language(locale)['RESPONSE'] + \
            f"{current_sentence}"
        
        #====================================================================
        # Visual components
        #====================================================================

        # prepare alignmen for display
        example_alignment_original_color = sentenceFunctions.color_alignment(example_alignment_original, example_alignment_answer)
        example_alignment_answer_color = sentenceFunctions.color_alignment(example_alignment_answer, example_alignment_original)
        
        with open ("./documents/apl_example.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "word_counter": f"{get_language(locale)['EXAMPLE_COUNTER']}",
                                "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (0)}", 
                                "current_word": f"<tt>{example_alignment_original_color}</tt>",
                                "current_answer": f"<tt>{example_alignment_answer_color}</tt>", 
                                "current_word_prompt": get_language(locale)['EXAMPLE_DISPLAY_CURRENT_ROUND_CHECK'],
                                "help": get_language(locale)['DISPLAY_PROMPT_TO_START_ROUND'],
                                "score": f"{get_language(locale)['DISPLAY_CURRNET_SCORE'] % (example_points, example_points_max)}",
                                "score_details": f"{get_language(locale)['DISPLAY_CURRENT_SCORE_DETAILS'] % (example_answer_score, example_penalty_score, example_points)}",
                                "score_explanation": f"{get_language(locale)['EXAMPLE_SCORE_EXPLANATION'] % (example_answer, example_word, example_points)}"
                            },
                            "assets" : {
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


def present_new_sentence(locale, round):
    if round == 0:
        pre = get_language(locale)['NEW_SENTENCE_PRE']
        options = get_language(locale)['NEW_SENTENCE_FIRST_OPTIONS']
        say = f"{random.choice(pre)}" +\
            f"{get_language(locale)['FIRST_ROUND']}" +\
            f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01'/>" +\
            f"{random.choice(options)}"
    
    if round in [1,2,3]:
        pre = get_language(locale)['NEW_SENTENCE_PRE']
        options = get_language(locale)['NEW_SENTENCE_MIDDLE_OPTIONS']
        say = f"{random.choice(pre)}" +\
            f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01'/>" +\
            f"{random.choice(options)}"
    
    if round == 4:
        pre = get_language(locale)['NEW_SENTENCE_PRE']
        options = get_language(locale)["NEW_SENTENCE_LAST_OPTIONS"]
        say = f"{random.choice(pre)}" +\
            f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01'/>" +\
            f"{random.choice(options)}"
    
    return say

def get_answer_round_ongoing(locale):
    answer = get_language(locale)['ANSWER_ONGOING']
    return random.choice(answer)

def get_answer(locale):
    answer = get_language(locale)['ANSWER']
    return random.choice(answer)


class StartRoundIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("StartRoundIntent")(handler_input)
            )
    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        session_attributes['in_round'] = True
        session_attributes['change_answer_possible'] = 1
        session_attributes['logg_answer_possible'] = 1
        session_attributes['continue_next_possible'] = 1
        ask_output = ''
        speak_output = ''
        
        
        # check if a question was already asked
        # -> prevents user to restart the round without answering
        if session_attributes['current_sentence'] is not None:
            
            if session_attributes['count_restarts'] < 2:
                speak_output = get_answer_round_ongoing(locale) + \
                    f"{session_attributes['current_sentence']} <break time='0.5s'/> " + \
                    get_answer(locale)
                ask_output = get_language(locale)['ACTION']
            
            if session_attributes['count_restarts'] >= 2:
                speak_output = get_answer_round_ongoing(locale) + \
                    f"{session_attributes['current_sentence']} <break time='0.5s'/> " + \
                    get_answer(locale) + \
                    get_language(locale)['PROMPT_TO_EXAMPLE']
                ask_output = get_language(locale)['ACTION']
            
            session_attributes['count_restarts'] = session_attributes['count_restarts'] + 1
            session_attributes['response'] = get_language(locale)['RESPONSE'] + \
                f"{session_attributes['current_sentence']} "
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )
        
        # reset restart counter
        session_attributes['count_restarts'] = 0
        
        # import sentenceFunctions and get a random sentence
        import sentenceFunctions
        sentence_library = sentenceFunctions.load_sentence_library(locale)
        current_sentence = sentenceFunctions.get_random_sentence_remove_past(sentence_library, session_attributes['past_sentences'])
        
        speak_output = present_new_sentence(locale, session_attributes['round_iteration_counter']) + \
            f"{current_sentence} " + \
            f" <break time='0.5s'/> " + \
            get_answer(locale) + \
            f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_01'/>"
            #f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_waiting_loop_30s_01'/>"
        
        ask_output = get_answer(locale)
        
        # store session_attributes
        session_attributes['played_games'] = session_attributes['played_games'] + 1
        session_attributes['current_sentence'] = current_sentence
        
        handler_input.attributes_manager.session_attributes = session_attributes
        
        # display card info
        card_title = get_language(locale)['CURRENT_SENTENCE_CARD_TITLE']
        card_text = current_sentence
        
        session_attributes['response'] = get_language(locale)['RESPONSE'] + \
            f"{current_sentence}"
        
        #====================================================================
        # Visual components
        #====================================================================
        
        display_round_counter = session_attributes['round_iteration_counter'] +1
        display_all_time_round_counter = session_attributes['played_games'] 
        display_current_word = current_sentence.upper()
        
        with open ("./documents/apl_in_round.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "word_counter": f"{get_language(locale)['DISPLAY_CURRENT_ROUND_COUNTER'] % (display_round_counter)}",
                                "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                "current_word": f"{display_current_word}",
                                "current_answer": "", # stays empty; there is no answer yet
                                "current_word_prompt": get_language(locale)['DISPLAY_CURRENT_WORD_HEADER'],
                                "current_answer_prompt": "", # stays empty; there is no answer yet
                                "help": get_language(locale)['DISPLAY_PROMPT_TO_ANSWER'],
                                "score": ""
                            },
                            "assets" : {
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        # set intent name for flow tracking
        #this_intent_name = ask_utils.get_intent_name(handler_input)
        #session_attributes['last_intent'] = this_intent_name
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .set_card(SimpleCard(card_title, card_text))
                .response
        )

class ChangedAnswerIntentHandler(AbstractRequestHandler):
    #option to repeat the sentence and/or tagged words
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input) 
            and ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input) 
            )
    
    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        # check if changing the answer is an option right now
        # -> 0 = not possible, because not round game yet
        # -> 1 = not possible, because no answer was given
        # -> 2 = not possible, because answer was already checked
        # -> 3 = possible
        if session_attributes['change_answer_possible'] == 0:
            speak_output = get_language(locale)['HELP_NO_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['change_answer_possible'] == 1:
            speak_output = get_language(locale)['HELP_IN_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['change_answer_possible'] == 2:
            speak_output = get_language(locale)['DISPLAY_PROMPT_NEXT_WORD']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        
        speak_output = f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_01'/>" + \
            f" {get_language(locale)['PROMPT_TO_ANSWER_CHANGE']}" 
        ask_output = get_language(locale)['ACTION']
        
        current_sentence = session_attributes['current_sentence']
        
        #====================================================================
        # Visual components
        #====================================================================
        
        display_round_counter = session_attributes['round_iteration_counter']
        display_all_time_round_counter = session_attributes['played_games'] 
        display_current_word = current_sentence.upper()
        
        with open ("./documents/apl_in_round.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "word_counter": f"{get_language(locale)['DISPLAY_CURRENT_ROUND_COUNTER'] % (display_round_counter)}",
                                "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                "current_word": f"{display_current_word}",
                                "current_answer": "", # stays empty; there is no answer yet
                                "current_word_prompt": get_language(locale)['DISPLAY_CURRENT_WORD_HEADER'],
                                "current_answer_prompt": "", # stays empty; there is no answer yet
                                "help": get_language(locale)['DISPLAY_PROMPT_TO_ANSWER'],
                                "score": ""
                            },
                            "assets" : {
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        session_attributes['answer_sentence'] == ""
        # setting flow control variables
        session_attributes['logg_answer_possible'] = 1
        session_attributes['continue_next_possible'] = 1
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )



def repeat_answer(locale):
    answer = get_language(locale)['REPEAT_ANSWER']
    return random.choice(answer)

def get_answer_logged_in(locale):
    answer = get_language(locale)["GET_ANSWER_LOGGED"]
    return random.choice(answer)


class GetAnswerIntentHandler(AbstractRequestHandler):
    #option to repeat the word to user
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input) 
            and ask_utils.is_intent_name("GetAnswerIntent")(handler_input) 
            )
    
    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['change_answer_possible'] = 3
        session_attributes['logg_answer_possible'] = 3
        session_attributes['continue_next_possible'] = 2
        
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        answer_sentence = ask_utils.request_util.get_slot(handler_input, "text").value
        speak_output = repeat_answer(locale) + \
            f"{answer_sentence}. " + \
            get_answer_logged_in(locale) 
            #f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_01'/>" 
        
        ask_output = get_language(locale)['GET_ANSWER_LOGGED_REPEAT']
        
        session_attributes['answer_sentence'] = answer_sentence
        session_attributes['response'] = get_language(locale)['RESPONSE'] + speak_output      
        
        #====================================================================
        # Visual components
        #====================================================================
        
        display_round_counter = session_attributes['round_iteration_counter'] +1
        display_all_time_round_counter = session_attributes['played_games']
        display_current_word = session_attributes['current_sentence'].upper()
        display_answer_word = answer_sentence.upper()
        
        with open ("./documents/apl_in_round.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "word_counter": f"{get_language(locale)['DISPLAY_CURRENT_ROUND_COUNTER'] % (display_round_counter)}",
                                "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                "current_word": f"{display_current_word}",
                                "current_answer": f"{display_answer_word}", 
                                "current_word_prompt": get_language(locale)['DISPLAY_CURRENT_WORD_HEADER'],
                                "current_answer_prompt": get_language(locale)['DISPLAY_CURRENT_ANSWER_HEADER'],
                                "help": get_language(locale)['DISPLAY_PROMPT_TO_LOGGIN'],
                                "score": ""
                            },
                            "assets" : {
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


def tell_score_result(locale, points, max_points):
    points_fraction = round(points / max_points, 2)
    if points_fraction < 0.3:
        answer = f"{random.choice(get_language(locale)['RESULT_SCORE_BAD']) % (points, max_points)}"
    if points_fraction >= 0.3 and points_fraction < 0.6:
        answer = f"{random.choice(get_language(locale)['RESULT_SCORE_MEDIUM']) % (points, max_points)}"
    if points_fraction >= 0.6:
        answer = f"{random.choice(get_language(locale)['RESULT_SCORE_GREAT']) % (points, max_points)}"
    return answer


class CheckAnswerIntentHandler(AbstractRequestHandler):
    #option to repeat the sentence and/or tagged words
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) 
            )

    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        
        # check if giving an answer is an option right now
        # -> 0 = not possible, because not round yet
        # -> 1 = not possible, because no word has been given yet
        # -> 2 = not possible, because answer was already checked
        # -> 3 = possible
        if session_attributes['logg_answer_possible'] == 0:
            speak_output = get_language(locale)['HELP_NO_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['logg_answer_possible'] == 1:
            speak_output = get_language(locale)['HELP_IN_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['logg_answer_possible'] == 2:
            speak_output = get_language(locale)['DISPLAY_PROMPT_NEXT_WORD']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        
        
        
        # check if answer is present
        if session_attributes['answer_sentence'] == "":
            
            speak_output = get_language(locale)["ANSWER_NOT_UNDERSTOOD"]
            session_attributes['response'] = get_language(locale)["RESPONSE"] + speak_output
            
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        
        
        # increment round counter
        session_attributes['round_iteration_counter'] = session_attributes['round_iteration_counter'] + 1
        
        # score answer sentence and get new random sentence for next round
        import sentenceFunctions
        current_result = sentenceFunctions.check_answer(session_attributes['current_sentence'], session_attributes['answer_sentence'])
        current_points = current_result[1]
        current_points_max = current_result[0]
        alignment_original = current_result[2]
        alignment_answer = current_result[3]
        current_penalty_score = current_result[4]
        current_answer_score = current_result[5]
        
        # update total score of this round
        total_points = session_attributes['total_points'] + current_points
        session_attributes['total_points'] = total_points
        
        total_points_max = session_attributes['total_points_max'] + current_points_max
        session_attributes['total_points_max'] = total_points_max
        
        # store the current sentence in past sentences
        past_sentences = session_attributes['past_sentences']
        past_sentences.append(session_attributes['current_sentence'])
        session_attributes['past_sentences'] = past_sentences
        
        # tell score to user and prompt to play next word
        speak_output = f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_01'/>" + \
            f"{tell_score_result(locale, current_points, current_points_max)}" + \
            f" <break time='0.5s'/> " + \
            get_language(locale)["ASK_NEXT_WORD"] 
        
        ask_output = get_language(locale)["ASK_NEXT_WORD"] 
        
        # flag if the user just repeated the question word
        if (session_attributes['current_sentence'].upper() == session_attributes['answer_sentence'].upper()):
            speak_output = f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_neutral_response_01'/>" + \
                f"{get_language(locale)['BASH_USER']}" + \
                f" <break time='0.5s'/> " + \
                get_language(locale)["ASK_NEXT_WORD"] 
            
            ask_output = get_language(locale)["ASK_NEXT_WORD"] 
        
        #====================================================================
        # Visual components
        #====================================================================
        
        display_round_counter = session_attributes['round_iteration_counter']
        display_all_time_round_counter = session_attributes['played_games']
        
        # prepare alignmen for display
        alignment_original_color = sentenceFunctions.color_alignment(alignment_original, alignment_answer)
        alignment_answer_color = sentenceFunctions.color_alignment(alignment_answer, alignment_original)
            
        with open ("./documents/apl_answer_check.json") as apl_doc:
            test_apl = json.load(apl_doc)
            
            if ask_utils.get_supported_interfaces(
                    handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        document = test_apl,
                        datasources = {
                            "text": {
                                "word_counter": f"{get_language(locale)['DISPLAY_CURRENT_ROUND_COUNTER'] % (display_round_counter)}",
                                "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                "current_word": f"<tt>{alignment_original_color}</tt>",
                                "current_answer": f"<tt>{alignment_answer_color}</tt>", 
                                "current_word_prompt": get_language(locale)['DISPLAY_CURRENT_ROUND_CHECK'],
                                "help": get_language(locale)['DISPLAY_PROMPT_NEXT_WORD'],
                                "score": f"{get_language(locale)['DISPLAY_CURRNET_SCORE'] % (current_points, current_points_max)}",
                                "score_details": f"{get_language(locale)['DISPLAY_CURRENT_SCORE_DETAILS'] % (current_answer_score, current_penalty_score, current_points)}"
                            },
                            "assets" : {
                                "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                            }
                        }
                    )
                )
        
        # store all results of the current round
        past_sentences = session_attributes['past_sentences']
        past_sentences.append(session_attributes['current_sentence'])
        session_attributes['past_sentences'] = past_sentences
        
        played_words_in_round = session_attributes['played_words_in_round']
        played_words_in_round.append(session_attributes['current_sentence'])
        session_attributes['played_words_in_round'] = played_words_in_round
        
        played_scores_in_round = session_attributes['played_scores_in_round']
        current_points_fract = round(current_points / current_points_max, 2) *5
        played_scores_in_round.append(current_points_fract)
        session_attributes['played_scores_in_round'] = played_scores_in_round
        
        played_total_score_in_round = session_attributes['played_total_score_in_round']
        played_total_score_in_round = played_total_score_in_round + current_points
        session_attributes['played_total_score_in_round'] = played_total_score_in_round
        
        played_max_score_in_round = session_attributes['played_max_score_in_round']
        played_max_score_in_round = played_max_score_in_round + current_points_max
        session_attributes['played_max_score_in_round'] = played_max_score_in_round
        
        session_attributes['current_points'] = current_points
        session_attributes['logg_answer_possible'] = 2
        session_attributes['change_answer_possible'] = 2
        session_attributes['continue_next_possible'] = 3
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


def select_end_message(locale, which):
    if which == 0:
        msg = get_language(locale)['DISPLAY_END_MESSAGE']
        msg = msg[0]
    if which == 1:
        msg = get_language(locale)['DISPLAY_END_MESSAGE']
        msg = msg[1]
    if which == 2:
        msg = get_language(locale)['DISPLAY_END_MESSAGE']
        msg = msg[2]
    return msg


class ContinueRoundIntentHandler(AbstractRequestHandler):
    #option to repeat the sentence and/or tagged words
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("AMAZON.NextIntent")(handler_input)
            )

    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        
        # check if moving on with next is an option here
        # -> 0 = not possible, because not round yet
        # -> 1 = not possible, because no word has been given yet
        # -> 2 = not possible, because answer was not yet checked
        # -> 3 = possible
        if session_attributes['continue_next_possible'] == 0:
            speak_output = get_language(locale)['HELP_NO_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['continue_next_possible'] == 1:
            speak_output = get_language(locale)['HELP_IN_ROUND']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        if session_attributes['continue_next_possible'] == 2:
            # after this changeing or logging the answer in is possible
            #session_attributes['logg_answer_possible'] = 3
            #session_attributes['change_answer_possible'] = 3
            speak_output = get_language(locale)['DISPLAY_PROMPT_TO_LOGGIN']
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        
        # check if answer is present
        if session_attributes['answer_sentence'] == "":
            
            speak_output = get_language(locale)["ANSWER_NOT_UNDERSTOOD"]
            session_attributes['response'] = get_language(locale)["RESPONSE"] + speak_output
            
            ask_output = get_language(locale)['ACTION']
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
            )
        
        # if the round is not finished, we continue with the next word
        if session_attributes['round_iteration_counter'] < 5:
            # we have to continue the current round
            import sentenceFunctions
            past_sentences = session_attributes['past_sentences']
            sentence_library = sentenceFunctions.load_sentence_library(locale)
            current_sentence = sentenceFunctions.get_random_sentence_remove_past(sentence_library, past_sentences)
            
            speak_output = present_new_sentence(locale, session_attributes['round_iteration_counter']) + \
                f"{current_sentence} " + \
                f" <break time='0.5s'/> " + \
                get_answer(locale) + \
                f"<audio src='soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_01'/>"
            
            ask_output = f"{get_language(locale)['PROMPT_TO_ANSWER']}"
            
            session_attributes['current_sentence'] = current_sentence
            
            # clear some variables for flow control
            session_attributes['current_points'] == 0
            
            #====================================================================
            # Visual components
            #====================================================================
            
            display_round_counter = session_attributes['round_iteration_counter'] 
            display_all_time_round_counter = session_attributes['played_games'] 
            display_current_word = current_sentence.upper()
            
            with open ("./documents/apl_in_round.json") as apl_doc:
                test_apl = json.load(apl_doc)
                
                if ask_utils.get_supported_interfaces(
                        handler_input).alexa_presentation_apl is not None:
                    handler_input.response_builder.add_directive(
                        RenderDocumentDirective(
                            document = test_apl,
                            datasources = {
                                "text": {
                                    "word_counter": f"{get_language(locale)['DISPLAY_CURRENT_ROUND_COUNTER'] % (display_round_counter)}",
                                    "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                    "current_word": f"{display_current_word}",
                                    "current_answer": "", # stays empty; there is no answer yet
                                    "current_word_prompt": get_language(locale)['DISPLAY_CURRENT_WORD_HEADER'],
                                    "current_answer_prompt": "", # stays empty; there is no answer yet
                                    "help": get_language(locale)['DISPLAY_PROMPT_TO_ANSWER'],
                                    "score": ""
                                },
                                "assets" : {
                                    "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                                }
                            }
                        )
                    )
        
        # if the round is finished, we wrap up and display the results
        if session_attributes['round_iteration_counter'] == 5:
            
            total_points = session_attributes['total_points']
            total_points_max = session_attributes['total_points_max']
            current_highscore = session_attributes['highscore']
            
            # if result was a new highscore
            if total_points >= current_highscore:
                
                # if result was the first highscore
                if current_highscore == 0:
                    speak_output = f"{get_language(locale)['ROUND_FINISH_FIRST_HIGHSCORE'] % (total_points, total_points_max)}" + \
                        get_language(locale)["ROUND_FINISH_LOG_FIRST_HIGHSCORE"] + \
                        get_language(locale)["ROUND_FINISH_PROMPT_NEW_ROUND_FIRST_HIGHSCORE"] 
                    ask_output = get_language(locale)['PROMPT_TO_CONTINUE'] + get_language(locale)['ACTION']
                    
                # if result was not the first highscore
                if current_highscore != 0:
                    speak_output = f"<audio src='soundbank://soundlibrary/sports/crowds/crowds_02'/> " + \
                        get_language(locale)["ROUND_FINISH_NEW_HIGHSCORE"] + \
                        f"{get_language(locale)['ROUND_FINISH_LOG_NEW_HIGHSCORE'] % (current_highscore, total_points)}" + \
                        get_language(locale)["ROUND_FINISH_PROMPT_NEW_ROUND_NEW_HIGHSCORE"] 
                    ask_output = get_language(locale)['PROMPT_TO_CONTINUE'] + get_language(locale)['ACTION']
                
                # store new highscore
                session_attributes['highscore'] = total_points
                display_current_end_message = select_end_message(locale, 1)
                end_screen = utils.create_presigned_url('Media/screen_win.png')
                
            # if result was no new highscore
            if total_points < current_highscore:
                
                # get distance to highscore
                score_difference = current_highscore - total_points
                
                # close to old highscore
                if score_difference <= 10:
                    speak_output = f"{get_language(locale)['ROUND_FINISH_NO_HIGHSCORE'] % (total_points, total_points_max)}" + \
                        f"{get_language(locale)['ROUND_FINISH_CLOSE_TO_HIGHSCORE'] % (current_highscore)}" 
                    ask_output = get_language(locale)['ACTION'] + \
                        get_language(locale)['PROMPT_TO_CONTINUE']
                display_current_end_message = select_end_message(locale, 0)
                        
                # far away from old highscore
                if score_difference > 10:
                    speak_output = f"{get_language(locale)['ROUND_FINISH_NO_HIGHSCORE'] % (total_points, total_points_max)}" + \
                        f"{get_language(locale)['ROUND_FINISH_FAR_FROM_HIGHSCORE'] % (current_highscore)}" 
                    ask_output = get_language(locale)['ACTION'] + \
                        get_language(locale)['PROMPT_TO_CONTINUE']
                display_current_end_message = select_end_message(locale, 2)
                
                end_screen = utils.create_presigned_url('Media/screen_loss.png')
                    
            
            #====================================================================
            # Visual components
            #====================================================================
            
            display_all_time_round_counter = session_attributes['played_games'] 
            
            display_played_words_in_round = session_attributes['played_words_in_round']
            display_played_scores_in_round = session_attributes['played_scores_in_round']
            
            display_played_total_score_in_round = session_attributes['played_total_score_in_round']
            display_played_max_score_in_round = session_attributes['played_max_score_in_round']
            display_percentage_score_in_round = round((display_played_total_score_in_round / display_played_max_score_in_round) *100, 0) 
            
            #speak_output = f"{display_played_scores_in_round[0], display_played_scores_in_round[1], display_played_scores_in_round[2], display_played_scores_in_round[3], display_played_scores_in_round[4]}"
            
            
            with open ("./documents/apl_end_of_round.json") as apl_doc:
                test_apl = json.load(apl_doc)
                
                if ask_utils.get_supported_interfaces(
                        handler_input).alexa_presentation_apl is not None:
                    handler_input.response_builder.add_directive(
                        RenderDocumentDirective(
                            document = test_apl,
                            datasources = {
                                "text": {
                                    "word_counter": f"{get_language(locale)['DISPLAY_ROUND_END']}",
                                    "all_round_counter": f"{get_language(locale)['DISPLAY_ALL_TIME_ROUND_COUNTER'] % (display_all_time_round_counter)}", 
                                    "word1": f"1. {display_played_words_in_round[0]}", 
                                    "word2": f"2. {display_played_words_in_round[1]}", 
                                    "word3": f"3. {display_played_words_in_round[2]}",
                                    "word4": f"4. {display_played_words_in_round[3]}",
                                    "word5": f"5. {display_played_words_in_round[4]}",
                                    "score1": f"{display_played_scores_in_round[0]}",
                                    "score2": f"{display_played_scores_in_round[1]}",
                                    "score3": f"{display_played_scores_in_round[2]}",
                                    "score4": f"{display_played_scores_in_round[3]}",
                                    "score5": f"{display_played_scores_in_round[4]}",
                                    "score_text": f"{get_language(locale)['DISPLAY_POINT_NAME']}",
                                    "round_end_message": f"{display_current_end_message}",
                                    "round_end_score": f"{get_language(locale)['DISPLAY_ROUND_END_SCORE'] % (display_played_total_score_in_round, display_played_max_score_in_round)}",
                                    "help": f"{get_language(locale)['DISPLAY_PROMPT_TO_START_ROUND']}"
                                },
                                "assets" : {
                                    "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png'),
                                    "vicURL": end_screen
                                }
                            }
                        )
                    )
            
            
            # clean up for new round
            session_attributes['current_sentence'] = None
            session_attributes['answer_sentence'] = ""
            session_attributes['total_points'] = 0
            session_attributes['round_iteration_counter'] = 0
            session_attributes['current_points'] = 0
            session_attributes['in_round'] = False
            session_attributes['cummulative_points'] = session_attributes['cummulative_points'] + total_points
            
            session_attributes['played_words_in_round'] = []
            session_attributes['played_scores_in_round'] = []
            session_attributes['played_total_score_in_round'] = 0
            session_attributes['played_max_score_in_round'] = 0
            
            session_attributes['change_answer_possible'] = 0
            session_attributes['logg_answer_possible'] = 0
            
            session_attributes['response'] = get_language(locale)["RESPONSE"] + speak_output      
            handler_input.attributes_manager.session_attributes = session_attributes
            
            return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )
        
        # set some variables for flow control
        session_attributes['answer_sentence'] = ""
        session_attributes['continue_next_possible'] = 1
        session_attributes['change_answer_possible'] = 1
        session_attributes['logg_answer_possible'] = 1
        
        session_attributes['response'] = get_language(locale)["RESPONSE"] + speak_output      
        handler_input.attributes_manager.session_attributes = session_attributes
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


class RepeatIntentHandler(AbstractRequestHandler):
    #option to repeat the sentence and/or tagged words
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)
            )

    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        
        speak_output = session_attributes['response']
        
        return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class GameStatisticsIntentHandler(AbstractRequestHandler):
    #option to repeat the sentence and/or tagged words
    def can_handle(self, handler_input):
        return (
            ask_utils.is_request_type("IntentRequest")(handler_input)
            and ask_utils.is_intent_name("GameStatisticsIntent")(handler_input)
            )

    def handle(self, handler_input):
        
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['change_answer_possible'] = 0
        locale = session_attributes['locale']
        speak_output = ''
        ask_output = ''
        
        if session_attributes['in_round'] == False:
            
            visits_to_display = session_attributes['visits']
            played_games_to_display = session_attributes['played_games']
            cummulative_points_to_display = session_attributes['cummulative_points']
            highscore_to_display = session_attributes['highscore']
            
            speak_output = f"{get_language(locale)['STATS_SUMMARY'] % (visits_to_display, played_games_to_display, cummulative_points_to_display, highscore_to_display)}"
            ask_output = get_language(locale)['ACTION'] 
            
            # manage repeat response
            session_attributes['response'] = get_language(locale)["RESPONSE"] + speak_output
            handler_input.attributes_manager.session_attributes = session_attributes
            
            #====================================================================
            # Visual components
            #====================================================================
            
            with open ("./documents/apl_stats.json") as apl_doc:
                test_apl = json.load(apl_doc)
                
                if ask_utils.get_supported_interfaces(
                        handler_input).alexa_presentation_apl is not None:
                    handler_input.response_builder.add_directive(
                        RenderDocumentDirective(
                            document = test_apl,
                            datasources = {
                                "text": {
                                    "title_header": f"{get_language(locale)['STATS_TITLE_HEADER']}",
                                    "title": f"{get_language(locale)['STATS_TITLE']}",
                                    "help": f"{get_language(locale)['DISPLAY_PROMPT_TO_START_ROUND']}",
                                    "features": [
                                        f"{get_language(locale)['STATS_FEATURES_GAMES_PLAYED'] % (visits_to_display)}",
                                        f"{get_language(locale)['STATS_FEATURES_ROUNDS_PLAYED'] % (played_games_to_display)}",
                                        f"{get_language(locale)['STATS_FEATURES_POINT_SCORE'] % (cummulative_points_to_display)}",
                                        f"{get_language(locale)['STATS_FEATURE_HIGHSCORE'] % (highscore_to_display)}"
                                    ]
                                },
                                "assets" : {
                                    "backgroundURL": utils.create_presigned_url('Media/wm_wallpaper.png')
                                }
                            }
                        )
                    )
            
            return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )
        else:
            speak_output = get_language(locale)['HELP_IN_ROUND']
            ask_output = get_language(locale)['ACTION'] 
            return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )



class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['change_answer_possible'] = 0
        locale = session_attributes['locale']
        
        if session_attributes['in_round'] == True:
            # we are in a around
            speak_output = get_language(locale)['HELP_IN_ROUND']
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
        else:
            # we are not in a round
            speak_output = get_language(locale)['HELP_NO_ROUND']
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        
        end_message = get_language(locale)['END']
        speak_output = random.choice(end_message)
        
        handler_input.response_builder.speak(speak_output).set_should_end_session(True)
        return handler_input.response_builder.response

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        
        if session_attributes['in_round'] == False:
            speak_output = get_language(locale)['HELP_NO_ROUND']
            
            logger.info("In FallbackIntentHandler")

            return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .ask(speak_output)
                        .response
                )
        else:
            speak_output = get_language(locale)['HELP_IN_ROUND']
            return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .ask(speak_output)
                        .response
                )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        
        return handler_input.response_builder.response

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        
        intent_name = ask_utils.get_intent_name(handler_input)
        
        speak_output = f"{get_language(locale)['INTENT_REFLECT'] % (intent_name)}"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        session_attributes = handler_input.attributes_manager.session_attributes
        locale = session_attributes['locale']
        
        logger.error(exception, exc_info=True)

        speak_output = get_language(locale)['EXCEPTION']
        speak_output = 'syntax or routing error'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class LoadDataInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        session_attributes = handler_input.attributes_manager.session_attributes
        
        locale = handler_input.request_envelope.request.locale
        
        if locale == "":
            locale = "en-US"
            session_attributes['locale'] = locale
        if not locale == "":
            session_attributes['locale'] = locale
        
        if 'visits' in persistent_attributes:
            session_attributes['visits'] = persistent_attributes['visits']
        else:
            session_attributes['visits'] = 0
        
        if 'played_games' in persistent_attributes:
            session_attributes['played_games'] = persistent_attributes['played_games']
        else:
            session_attributes['played_games'] = 0
        
        if 'current_sentence' not in session_attributes:
            session_attributes["current_sentence"] = None
            
        if 'count_restarts' not in session_attributes:
            session_attributes['count_restarts'] = 0
        
        if 'answer_sentence' not in session_attributes:
            session_attributes['answer_sentence'] = ""
            
        if 'round_iteration_counter' not in session_attributes:
            session_attributes['round_iteration_counter'] = 0
        
        if 'total_points' not in session_attributes:
            session_attributes['total_points'] = 0
        
        if 'total_points_max' not in session_attributes:
            session_attributes['total_points_max'] = 0  
        
        if 'highscore' in persistent_attributes:
            session_attributes['highscore'] = persistent_attributes['highscore']
        else:
            session_attributes['highscore'] = 0
        
        if 'cummulative_points' in persistent_attributes:
            session_attributes['cummulative_points'] = persistent_attributes['cummulative_points']
        else:
            session_attributes['cummulative_points'] = 0
        
        if 'past_sentences' not in session_attributes:
            session_attributes['past_sentences'] = []
        
        if 'in_round' not in session_attributes:
            session_attributes['in_round'] = False
        
        if 'response' not in session_attributes:
            session_attributes['response'] = "There is nothing to repeat"
        
        if 'played_words_in_round' not in session_attributes:
            session_attributes['played_words_in_round'] = []
        
        if 'played_scores_in_round' not in session_attributes:
            session_attributes['played_scores_in_round'] = []
        
        if 'played_total_score_in_round' not in session_attributes:
            session_attributes['played_total_score_in_round'] = 0
        
        if 'played_max_score_in_round' not in session_attributes:
            session_attributes['played_max_score_in_round'] = 0
        
        if 'current_points' not in session_attributes:
            session_attributes['current_points'] = 0
        
        if 'current_points_max' not in session_attributes:
            session_attributes['current_points_max'] = 0
        
        if 'change_answer_possible' not in session_attributes:
            session_attributes['change_answer_possible'] = 0
        
        if 'logg_answer_possible' not in session_attributes:
            session_attributes['logg_answer_possible'] = 0
            
        if 'continue_next_possible' not in session_attributes:
            session_attributes['continue_next_possible'] = 0


class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug('----- REQUEST -----')
        logger.debug("{}".format(
            handler_input.request_envelope.request))

class SaveDataInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        session_attributes = handler_input.attributes_manager.session_attributes

        persistent_attributes["visits"] = session_attributes["visits"]
        persistent_attributes["played_games"] = session_attributes["played_games"]
        persistent_attributes['highscore'] = session_attributes['highscore']
        persistent_attributes['cummulative_points'] = session_attributes['cummulative_points']
        
        handler_input.attributes_manager.save_persistent_attributes()

class LoggingResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug('----- RESPONSE -----')
        logger.debug("{}".format(response))

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter)
# custom
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetExampleIntentHandler()) 
sb.add_request_handler(StartRoundIntentHandler())
sb.add_request_handler(ChangedAnswerIntentHandler())
sb.add_request_handler(GetAnswerIntentHandler())
sb.add_request_handler(CheckAnswerIntentHandler())
sb.add_request_handler(ContinueRoundIntentHandler())
sb.add_request_handler(RepeatIntentHandler()) 
sb.add_request_handler(GameStatisticsIntentHandler()) 
# basic
sb.add_request_handler(HelpIntentHandler()) 
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
# end
sb.add_exception_handler(CatchAllExceptionHandler())
# interceptors
sb.add_global_request_interceptor(LoadDataInterceptor())
sb.add_global_request_interceptor(LoggingRequestInterceptor())
sb.add_global_response_interceptor(SaveDataInterceptor())
sb.add_global_response_interceptor(LoggingResponseInterceptor())
lambda_handler = sb.lambda_handler()
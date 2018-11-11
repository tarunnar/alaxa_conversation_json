import math
import datetime
import time
import os
import logging
import boto3
from boto3 import Session
import json
import re
import requests
import urllib
import random
from pprint import pprint
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def build_PlainSpeech(output_speech_text=None):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = output_speech_text
    return speech

def build_ssml_speech_object(json_dict=None):
    speech = {}
    speech['type'] = 'SSML'
    if json_dict!=None:
        speech['ssml'] = dict_to_ssml(json_dict)
    return speech



def build_total_response(version="1.0", session_attributes={}, response_object=None):
    total_response = {}
    total_response['version'] = version
    total_response['sessionAttributes'] = session_attributes
    total_response['response'] = response_object
    return total_response


def build_SimpleCard(title=None, body=None):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card

def build_standard_response_card(title=None, text=None, image=None):
    card = {}
    card['type'] = 'standard'
    card['title'] = title
    card['text'] = text
    return card



##############################
# Responses
##############################

def build_response_objects(output_speech_object=None, should_end_session=False, directives=None, response_card=None, reprompt_object=None):
    response_object={}
    response_object["outputSpeech"] = output_speech_object
    response_object["shouldEndSession"] = should_end_session
    response_object["directives"] = directives
    if response_card!=None:
        response_object["card"]=response_card
    if reprompt_object!=None:
        response_object["reprompt"]=reprompt_object
    return response_object

def build_directives(types=None, slot_to_elicit=None, updated_intent=None):
    to_add_directive_list=[]
    to_add_directive_json={}
    if types=="Dialog.Delegate":
        to_add_directive_json["type"]=types
        if updated_intent is not None:
            to_add_directive_json["updatedIntent"]=updated_intent
        to_add_directive_list.append(to_add_directive_json)
        return to_add_directive_list
    elif types=="Dialog.ElicitSlot":
        to_add_directive_json["type"]=types
        to_add_directive_json["slotToElicit"]=slot_to_elicit
        to_add_directive_json["updatedIntent"]=updated_intent
        to_add_directive_list.append(to_add_directive_json)
        return to_add_directive_list
    else:
        return None

def build_reprompt_object(output_speech_type="PlainText", output_speech_text=None):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = output_speech_text
    to_return={}
    to_return["outputSpeech"] = speech
    return to_return

def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_total_response( session_attributes={}, response_object= speechlet)


def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False

    return build_total_response( session_attributes={}, response_object= speechlet)



def elicit_slot(session_attributes={}, card_type=None, output_speech_type="PlainText", output_speech_text=None, output_speech_json=None, slot_to_elicit=None, updated_intent=None, should_end_session=False, card_title=None, card_body=None, reprompt_text=None):
    #print(card_body,card_title)
    output_speech_object=None
    if output_speech_type=="PlainText":
        output_speech_object=build_PlainSpeech(output_speech_text=output_speech_text)
    else:
        if output_speech_json is not None:
            output_speech_object=build_ssml_speech_object(json_dict=output_speech_json)
        else:
            logger.debug("not got output_speech_json for ssml creation")
    card_object=None
    if card_type=="Simple":
        if card_title!=None and card_body!=None:
            card_object=build_SimpleCard(title=card_title, body=card_body)
        else:
            logger.debug("not got title or body for simple card")
    elif card_type=="Standard":
        if card_title!=None and output_speech_json!=None:
            card_object=build_standard_response_card(title=None, text=json.dumps(output_speech_json))
        else:
            logger.debug("not got title or output_speech_json for simple card")
    else:
        logger.debug("No card type given")
    directives=build_directives(types="Dialog.ElicitSlot",slot_to_elicit= slot_to_elicit, updated_intent=updated_intent)
    reprompt_object=None
    if reprompt_text!=None:
        reprompt_object=build_reprompt_object(output_speech_type = "PlainText", output_speech_text = reprompt_text)
    response_object=build_response_objects(output_speech_object=output_speech_object, should_end_session=should_end_session, directives=directives, response_card=card_object, reprompt_object=reprompt_object)
    to_return=build_total_response(session_attributes=session_attributes, response_object= response_object)
    return to_return

def delegate(session_attributes={}, should_end_session=False, output_speech_text=None, updated_intent =None):
    directives= build_directives(types= "Dialog.Delegate", updated_intent=updated_intent)
    response_object = {}
    response_object['shouldEndSession'] = should_end_session 
    response_object['directives'] = directives
    if output_speech_text is not None:
        output_speech_object=build_PlainSpeech(output_speech_text=output_speech_text)
        response_object["outputSpeech"]=output_speech_object
    to_return = build_total_response(session_attributes=session_attributes, response_object=response_object)
    return to_return


##############################
# Required Intents
##############################


def cancel_intent():
    return statement("CancelIntent", "You want to cancel")  #don't use CancelIntent as title it causes code reference error during certification 


def help_intent():
    return statement("CancelIntent", "You want help")       #same here don't use CancelIntent


def stop_intent():
    return statement("StopIntent", "You want to stop")      #here also don't use StopIntent

def on_launch(event, context):
    return statement("title", "Hi I am pencilman I can help you in accesing edu content do you want to proceed")

############################################################
def getIntent(event):
    return event["request"]["intent"]

def getSessionAttributes(event):
    if "attributes" in event["session"].keys():
        return event["session"]["attributes"]
    else:
        return {}



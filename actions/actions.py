import os
from typing import Any, Text, Dict, List
from dotenv import load_dotenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

import pandas as pd
import google.generativeai as genai

gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)

def generate_summary(text):

    df = pd.read_csv(text)
    text_data = df.to_string(index=False)

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content('Summarize this table and provide insights:\n' +text_data)

    return response.text

class ActionSaveContact(Action):

    def name(self) -> Text:
        return "action_save_contact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name = tracker.get_slot('name')
        email = tracker.get_slot('email')
        phone = tracker.get_slot('phone')

        contact_data = f"{name},{email},{phone}\n"
        with open('output/contacts.csv', 'a') as f:
            f.write(contact_data)

        dispatcher.utter_message(text=f"Contact details saved: Name={name}, Email={email}, Phone={phone}")

        return []

class ActionDocSummarize(Action):

    def name(self) -> Text:
        return "action_doc_summarize"

    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            csv_file = open("input/moredata.csv", "r")
            if csv_file is None:
                dispatcher.utter_message(text="Sorry, I couldn't find the uploaded file. Please try uploading the file again.")
                return []
            
            file_path = "input/moredata.csv"
            summary = generate_summary(file_path)

            dispatcher.utter_message(text=summary)
            dispatcher.utter_message(text="Thank you for using our chatbot. Do you have any other questions?")
        except Exception as e:
            dispatcher.utter_message(text=f"Error: {e}")

        return []

class ValidateContactForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_contact_form"

    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Validate name value."""
        # Add validation logic here if necessary
        return {"name": slot_value}

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Validate email value."""
        # Add validation logic here if necessary
        return {"email": slot_value}

    def validate_phone(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Validate phone value."""
        # Add validation logic here if necessary
        return {"phone": slot_value}

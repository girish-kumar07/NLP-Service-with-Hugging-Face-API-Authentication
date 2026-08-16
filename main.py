"""
main.py
Entry point for the NLP App. Handles the CLI menu flow and connects
the database, auth, and NLP service layers.
"""

import logging

from database import Database
from auth import AuthManager
from nlp_service import NLPService, NLPServiceError

# --- Logging setup ---
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class NLPApp:
    def __init__(self):
        self.db = Database()
        self.auth = AuthManager(self.db)
        self.current_user_email = None
        self.current_user_name = None
        self._nlp_service = None  # created lazily, only once logged in

    @property
    def nlp_service(self):
        """Lazily initialize the NLP service so the app doesn't crash on
        startup if the API key isn't set yet — only when it's actually used."""
        if self._nlp_service is None:
            self._nlp_service = NLPService()
        return self._nlp_service

    def run(self):
        self._first_menu()

    # ---------- Menus ----------

    def _first_menu(self):
        choice = input("""
        Hi! How would you like to proceed?
        1. Not a member? Register
        2. Already a member? Login
        3. Entered by mistake? Exit
        Enter your choice: """).strip()

        if choice == "1":
            self._register_flow()
        elif choice == "2":
            self._login_flow()
        elif choice == "3":
            print("Goodbye!")
            return
        else:
            print("Invalid input. Please try again.")
            self._first_menu()

    def _second_menu(self):
        choice = input(f"""
        Hi {self.current_user_name}! How would you like to proceed?
        1. Named Entity Recognition (NER)
        2. Language Detection
        3. Sentiment Analysis
        4. Logout
        Enter your choice: """).strip()

        if choice == "1":
            self._ner_flow()
        elif choice == "2":
            self._language_detection_flow()
        elif choice == "3":
            self._sentiment_analysis_flow()
        elif choice == "4":
            logging.info(f"User logged out: {self.current_user_email}")
            self.current_user_email = None
            self.current_user_name = None
            print("Logged out successfully.")
            self._first_menu()
        else:
            print("Invalid input. Please try again.")
            self._second_menu()

    # ---------- Auth flows ----------

    def _register_flow(self):
        name = input("Enter Name: ").strip()
        email = input("Enter E-mail: ").strip()
        password = input("Enter Password: ").strip()

        success, message = self.auth.register(name, email, password)
        print(message)

        if success:
            logging.info(f"New user registered: {email}")
            self._first_menu()
        elif "already registered" in message:
            choice = input("""
            1. Login instead
            2. Try registering again
            3. Exit
            Enter your choice: """).strip()
            if choice == "1":
                self._login_flow()
            elif choice == "2":
                self._register_flow()
            else:
                print("Goodbye!")
        else:
            self._register_flow()

    def _login_flow(self):
        email = input("Enter your E-mail: ").strip()
        password = input("Enter Password: ").strip()

        success, message, name = self.auth.login(email, password)
        print(message)

        if success:
            logging.info(f"User logged in: {email}")
            self.current_user_email = email
            self.current_user_name = name
            self._second_menu()
        else:
            self._first_menu()

    # ---------- NLP flows ----------

    def _sentiment_analysis_flow(self):
        text = input("Enter the paragraph: ")
        try:
            label = self.nlp_service.analyze_sentiment(text)
            print(f"Detected emotion: {label}")
        except NLPServiceError as e:
            print(f"Error: {e}")
            logging.error(f"Sentiment analysis failed: {e}")
        self._second_menu()

    def _ner_flow(self):
        text = input("Enter the paragraph: ")
        try:
            entities = self.nlp_service.extract_entities(text)
            if entities:
                print("Entities found:")
                for entity_text, entity_type in entities:
                    print(f"  - {entity_text} ({entity_type})")
            else:
                print("No entities found.")
        except NLPServiceError as e:
            print(f"Error: {e}")
            logging.error(f"NER failed: {e}")
        self._second_menu()

    def _language_detection_flow(self):
        text = input("Enter the paragraph: ")
        try:
            lang = self.nlp_service.detect_language(text)
            print(f"Detected language: {lang}")
        except NLPServiceError as e:
            print(f"Error: {e}")
            logging.error(f"Language detection failed: {e}")
        self._second_menu()


if __name__ == "__main__":
    app = NLPApp()
    app.run()
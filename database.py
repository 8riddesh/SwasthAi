# database.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseClient:
    def __init__(self):
        url = "https://neogntmtnlmyrcirpiot.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lb2dudG10bmxteXJjaXJwaW90Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU1NzA0MjEsImV4cCI6MjA2MTE0NjQyMX0.8OXu90tC9fKofrVtS5aN6aA5-e9vlWmoet4Sy0T7vBE"
        if not url or not key:
            raise ValueError("Missing Supabase URL or key. Add them to your .env file.")
        self.client = create_client(url, key)

    def create_user(self, user_data):
        """Insert user personal info into the users table"""
        try:
            response = self.client.table('users1').insert({
                'email': user_data['email'],
                'password_hash': user_data['password_hash'],
                'full_name': user_data['full_name'],
                'age': user_data['age'],
                'gender': user_data['gender'],
                'contact_no': user_data['contact_no']
            }).execute()

            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def create_medical_info(self, user_id, conditions):
        """Insert user medical conditions into the medical_info table"""
        try:
            # Insert standard conditions
            for condition_name, has_condition in conditions['standard'].items():
                if has_condition:
                    self.client.table('medical_info').insert({
                        'user_id': user_id,
                        'condition_name': condition_name,
                        'condition_type': 'standard'
                    }).execute()

            # Insert custom conditions
            for condition in conditions['custom']:
                if condition.strip():  # Only insert non-empty conditions
                    self.client.table('medical_info').insert({
                        'user_id': user_id,
                        'condition_name': condition,
                        'condition_type': 'custom'
                    }).execute()
            medical_id=self.client.table('medical_info').select('id').eq('user_id',user_id).execute()
            return True
        except Exception as e:
            print(f"Error creating medical info: {e}")
            return False

    def get_user_by_email(self, email):
        """Retrieve user by email for login"""
        try:
            response = self.client.table('users1').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Retrieve user by ID for profile display/update"""
        try:
            response = self.client.table('users1').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            response = self.client.table('users1').update(update_data).eq('id', user_id).execute()
            return True if response.data else False
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def update_medical_info(self, user_id, conditions):
        """Update user medical conditions"""
        try:
            # First delete all existing conditions
            self.client.table('medical_info').delete().eq('user_id', user_id).execute()
            
            # Then create new ones
            self.create_medical_info(user_id, conditions)
            return True
        except Exception as e:
            print(f"Error updating medical info: {e}")
            return False

    def get_user_medical_info(self, user_id):
        """Retrieve user medical conditions"""
        try:
            response = self.client.table('medical_info').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting medical info: {e}")
            return []

    def save_chat(self, user_id, question, answer):
        """Save chat history for a user"""
        try:
            response = self.client.table('chat_history').insert({
                'user_id': user_id,
                'question': question,
                'answer': answer,
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving chat: {e}")
            return False

    def get_chat_history(self, user_id):
        """Retrieve chat history for a user"""
        try:
            response = self.client.table('chat_history').select('*').eq('user_id', user_id).order('created_at',
                                                                                                  desc=False).execute()
            return response.data
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
            
    # FUNCTIONS FOR EMOTIONAL DIARY
    
    def save_emotional_diary_entry(self, user_id, entry, response, mood, json_data):
        """Save emotional diary entry for a user"""
        try:
            response_data = self.client.table('emotional_diary').insert({
                'user_id': user_id,
                'entry': entry,
                'response': response,
                'mood': mood,
                'json_data': json_data
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving diary entry: {e}")
            return False

    def get_emotional_diary_history(self, user_id):
        """Retrieve emotional diary history for a user"""
        try:
            response = self.client.table('emotional_diary').select('*').eq('user_id', user_id).order('created_at',
                                                                                            desc=False).execute()
            return response.data
        except Exception as e:
            print(f"Error getting diary history: {e}")
            return []
            
    def delete_emotional_diary_entry(self, entry_id):
        """Delete a specific emotional diary entry"""
        try:
            self.client.table('emotional_diary').delete().eq('id', entry_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting diary entry: {e}")
            return False
            
    # NEW FUNCTIONS FOR DOCUMENT MANAGEMENT
    
    def save_document(self, user_id, file_name, extracted_text, summary, medicines):
        """Save document information to the database"""
        try:
            response = self.client.table('user_documents').insert({
                'user_id': user_id,
                'file_name': file_name,
                'extracted_text': extracted_text,
                'summary': summary,
                'medicines': medicines
            }).execute()
            return True
        except Exception as e:
            print(f"Error saving document: {e}")
            return False
            
    def get_user_documents(self, user_id):
        """Retrieve documents for a user"""
        try:
            response = self.client.table('user_documents').select('*').eq('user_id', user_id).order('created_at', 
                                                                                              desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []
            
    def get_document_by_id(self, document_id):
        """Retrieve a specific document by ID"""
        try:
            response = self.client.table('user_documents').select('*').eq('id', document_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting document by ID: {e}")
            return None
            
    def delete_document(self, document_id):
        """Delete a document from the database"""
        try:
            self.client.table('user_documents').delete().eq('id', document_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
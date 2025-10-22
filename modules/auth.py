import json
import os
import streamlit as st
from hashlib import sha256

USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Utente già esistente."
    users[username] = {"password": hash_password(password)}
    save_users(users)
    return True, "Registrazione completata!"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Utente non trovato."
    if users[username]["password"] != hash_password(password):
        return False, "Password errata."
    return True, "Accesso eseguito!"

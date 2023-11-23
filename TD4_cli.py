# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 15:46:49 2023

@author: aikan
"""

import requests

BASE_URL = "http://localhost:8000"

def get_jwt_token():
    auth_url = f"{BASE_URL}/token"
    response = requests.post(auth_url, data={"username": "amartin", "password": "password_2"})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Erreur:", response.status_code, response.text)
        raise ValueError("Authentification échouée")


def get_indicator_data(endpoint, token):
    """Fonction pour obtenir les données d'un indicateur financier."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur:", response.status_code, response.text)
        return None


# Obtenir le JWT token
token = get_jwt_token()

# Obtenir les données RSI
rsi_data = get_indicator_data("indicators/rsi", token)
print("RSI Data:", rsi_data)

# Obtenir les données MACD
macd_data = get_indicator_data("indicators/macd", token)
print("MACD Data:", macd_data)


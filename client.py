import httpx

# Remplacez par l'URL de votre API
url = "http://127.0.0.1:8000"

# Demande d'authentification pour obtenir un token JWT
auth_data = {'username': 'john', 'password': 'hello'}
auth_response = httpx.post(url + "/token", data=auth_data)

# Imprimer le token
print(f"Response: {auth_response.json()}")

# Vérifiez si l'authentification a réussi (code de statut 200 OK)
if auth_response.is_success:
    # Obtenez le token d'accès
    access_token = auth_response.json().get('access_token')
    if access_token:
        # Ajoutez le token d'accès aux en-têtes de la requête pour la route protégée
        headers = {'Authorization': f'Bearer {access_token}'}

        # Faites une requête à la route protégée /test
        test_response = httpx.get(url + "/test", headers=headers)

        # Vérifiez si l'accès à la route protégée réussit
        if test_response.is_success:
            print("Access to protected route successful")
            print(test_response.json())
        else:
            print(f"Failed to access protected route. Status code: {test_response.status_code}")
            print(test_response.text)
    else:
        print("Failed to obtain access token from authentication response.")
else:
    print(f"Failed to authenticate. Status code: {auth_response.status_code}")

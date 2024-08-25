import json
import requests



class  mcp:
    async def mcp(accunt_id ,  body , token , operation , profil):
                url = f"https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/game/v2/profile/{accunt_id}/client/{operation}?profileId={profil}&rvn-1"
                headers = {
            "Content-Type": f"application/json",
            "Authorization": f"Bearer {token}"
        }
                semijson = json.dumps(body)
                data = json.loads(semijson)
                print(data)
                response = requests.post(url, headers=headers, data=data)
                daata = response.json()
                return daata
    

    async def savequest(acunt_id, token):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        url = f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{acunt_id}/client/ClientQuestLogin?profileId=campaign&rvn=-1"

        payload = {}

    
    
        response = requests.post(url, headers=headers, json=payload)  

        return response.status_code
    

            
    async def lookup(displayname,token):
           url = f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/displayName/{displayname}"
           headers = {
            "Content-Type": f"application/json",
            "Authorization": f"Bearer {token}"
        }
           r = requests.get(url=url , headers=headers)
           return r.json()
    
    async def getokenn(accuntid, diviceid, secret):
        auth_url = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token"
        auth_form_data = {
            "grant_type": "device_auth",
            "device_id": diviceid,
            "account_id": accuntid,
            "secret": secret
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE='
        }

        # Envoyer la requête POST
        auth = requests.post(url=auth_url, headers=headers, data=auth_form_data)

        # Vérifier si la requête est réussie
        if auth.status_code == 200:
            access_token = auth.json().get("access_token")
            return access_token
        else:
            print("Erreur: Échec de la récupération du token")
            return None
    
    
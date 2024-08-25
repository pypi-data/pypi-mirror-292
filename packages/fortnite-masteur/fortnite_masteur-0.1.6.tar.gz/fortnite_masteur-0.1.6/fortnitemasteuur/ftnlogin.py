import requests
import json
SWITCHTOKEN = "OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"
IOS_TOKEN = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="

class login:
    async def loginauthcode(code):
        HeaderData = {
                    "Content-Type": f"application/x-www-form-urlencoded",
                    "Authorization": f"basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
                }
        LoginData = f"grant_type=authorization_code&code={code}"
        hum = requests.post("https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",headers=HeaderData,data=LoginData)
        data = hum.json()
        name = data['displayName']
        account_id = data['account_id']
        token = data['access_token']

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(url=f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{account_id}/deviceAuth', headers=headers)
        daata = response.json()
        device_id, secret = daata['deviceId'], daata['secret']
        return device_id , secret , name , account_id
    



    async def creatcode():
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3"
        }
        body = {
            "grant_type": "client_credentials"
        }
        lol = requests.post(url=url , headers=headers ,  data = body)
        if lol.status_code != 200:
            return False


        data = lol.json()
        access_token = data.get("access_token")
        k = requests.post(
        url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization",
        headers={
                "Authorization": f"bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
    ) 
        data = await k.json()       
        return data["verification_uri_complete"], data["device_code"]




    async def claimcode(code):

    
                kk =  requests.post(
                    url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                    headers={
                        "Authorization": f"basic {SWITCHTOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "grant_type": "device_code",
                        "device_code": code
                    }
                )
                
              
                token = await kk.json()
                print(token)
                
                if kk.status_code == 200:
                    print("hum")
                else:
                    if token.get('errorCode') == 'errors.com.epicgames.account.oauth.authorization_pending':
                        pass
                    elif token.get('errorCode') == 'errors.com.epicgames.not_found':
                        pass
                    else:
                        print(json.dumps(token, sort_keys=False, indent=4))


                lol =  requests.get(
                    method="GET",
                    url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
                    headers={
                        "Authorization": f"bearer {token['access_token']}"
                    }
                ) 
                exchange = await lol.json()

                jj = requests.post(
                    url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                    headers={
                        "Authorization": f"basic {IOS_TOKEN}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={
                        "grant_type": "exchange_code",
                        "exchange_code": exchange['code']
                    }
                ) 
                auth_information = await jj.json()
                return auth_information
    
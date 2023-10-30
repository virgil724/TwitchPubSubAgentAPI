import json
import os
import yaml
import requests
import random



def getAccessTokenUsername():
    projectId = ""
    supabaseKey = ""
    url = f"https://{projectId}.supabase.co/rest/v1/TwitchToken"
    querystring = {"select": "access_token,profiles(username)"}
    headers = {
        "apikey": supabaseKey,
        "authorization": f"Bearer {supabaseKey}",
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def getIdwithLogin(token, logins):
    url = "https://api.twitch.tv/helix/users"

    querystring = {"login": logins}

    headers = {
        "authorization": f"Bearer {token}",
        "client-id": os.getenv("TWITCH_CLIENT_ID"),
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code==200:
        return [(i["login"], i["id"]) for i in response.json()["data"]]
    else:
        raise Exception(f"{response.json()["error"]} message:{response.json()["message"]}")


def validateToken(token):
    print("Token Validate Progress")
    url = "https://id.twitch.tv/oauth2/validate"

    headers = {
        'authorization': f"OAuth {token}"
        }

    response = requests.request("GET", url, headers=headers)

    if response.status_code==200:
        return True
    return False




def refreshToken(oldToken: str):
    APIKEY = os.getenv("APIKEY")
    ROOTURL = os.getenv("ROOTURL")
    headers = {
        "apikey": APIKEY,
        "authorization": f"Bearer {APIKEY}",
    }
    payload = json.dumps({"oldToken": oldToken})
    requests.post(f"{ROOTURL}/functions/v1/oauth_flow/refresh", headers=headers, data=payload)


def deleteToken(oldToken: str):
    APIKEY = os.getenv("APIKEY")
    ROOTURL = os.getenv("ROOTURL")
    url = f"{ROOTURL}/rest/v1/TwitchToken"

    querystring = {"access_token": oldToken}

    headers = {
        "apikey": APIKEY,
        "authorization": f"Bearer {APIKEY}",
    }

    response = requests.request("DELETE", url, headers=headers, params=querystring)

    if response.ok == True:
        return True
    return False

if __name__=="main":
    with open("docker-compose.yml", "r") as stream:
        data = yaml.safe_load(stream)


    accesstoken = getAccessTokenUsername()

    allneeded = [
        {"access_token": item["access_token"], "login": item["profiles"]["username"]}
        for item in accesstoken
        if item["profiles"]["username"]
    ]
    logins = [item["login"] for item in allneeded]
    login_id = getIdwithLogin(random.choice(allneeded)["access_token"], logins)
    ## update id to all needed
    for d in allneeded:
        login = d["login"]
        for login_id in login_id:
            if login == login_id[0]:
                d["id"] = login_id[1]

    services = {}
    for item in allneeded:
        token = item["access_token"]
        channelId = item["id"]

        example = {
            "image": "192.168.88.190/TwitchConnectClient:latest",
            "environment": [f"token={token}", f"channelId={channelId}"],
        }
        services.update({f"TwichPubSub_{channelId}": example})
    data["services"] = services
    # Remove Ref From Python
    # https://stackoverflow.com/questions/51272814/python-yaml-dumping-pointer-references
    yaml.Dumper.ignore_aliases = lambda *args: True
    with open("test.yaml", "w") as f:
        yaml.dump(data, f)


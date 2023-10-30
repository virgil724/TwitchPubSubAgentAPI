import secrets, os, requests, json

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from dotenv import load_dotenv

from docker_utils import docker_create, docker_delete, docker_update
from model import Action, TokenLogin, TokenLoginAction, TokenLoginId
from compose import getIdwithLogin, validateToken


load_dotenv()
token = os.getenv("TOKEN")
APIKEY = os.getenv("APIKEY")
ROOTURL = os.getenv("ROOTURL")
app = FastAPI()
header_scheme = APIKeyHeader(name="x-key")


def check_api_key(key: str = Security(header_scheme)):
    correct_key = secrets.compare_digest(key, token)
    if not correct_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )
    else:
        return key


def refreshToken(oldToken: str):
    headers = {
        "apikey": APIKEY,
        "authorization": f"Bearer {APIKEY}",
    }
    payload = json.dumps({"oldToken": oldToken})
    requests.post(f"{ROOTURL}/functions/v1/oauth_flow", headers=headers, data=payload)


def deleteToken(oldToken: str):
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


def CreateTLD(TL: TokenLogin):
    try:
        login_id = getIdwithLogin(TL.token, [TL.login])
    except Exception as e:
        print(e)
        try:
            refreshToken(TL.token)
            raise HTTPException(
                detail="Token Been Refresh", status_code=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            print(e)
            if deleteToken(TL.token):
                raise HTTPException(detail="Token Expired", status_code=400)
    numbers = [t[1] for t in login_id]
    loginid = numbers[0]
    TLD = TokenLoginId(**TL.model_dump(), login_id=loginid)
    return TLD


@app.post("/twitch_list")
def container_modified(TL: TokenLoginAction, key: str = Depends(check_api_key)):
    match TL.action:
        case Action.New:
            TLD = CreateTLD(TL)
            if not validateToken(TL.token):
                raise HTTPException(
                    detail="Token not validate", status_code=status.HTTP_400_BAD_REQUEST
                )

            try:
                docker_create(TLD)
                return {"result": "success"}
            except Exception as e:
                raise HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

        case Action.Delete:
            docker_delete(TL.login)

        case Action.Update:
            try:
                docker_update(TL)
                return {"result": "success"}
            except Exception as e:
                raise HTTPException(detail=e, status_code=status.HTTP_400_BAD_REQUEST)

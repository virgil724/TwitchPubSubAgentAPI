import secrets, os

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from dotenv import load_dotenv

from docker_utils import docker_create, docker_delete, docker_update
from model import Action, TokenLogin, TokenLoginAction, TokenLoginId
from compose import getIdwithLogin, validateToken



load_dotenv()
token = os.getenv("TOKEN")
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


def CreateTLD(TL: TokenLogin):
    login_id = getIdwithLogin(TL.token, [TL.login])
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

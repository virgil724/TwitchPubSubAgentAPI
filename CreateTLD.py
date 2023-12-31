from compose import getIdwithLogin, refreshToken, deleteToken
from model import TokenLogin, TokenLoginId


from fastapi import HTTPException, status


def CreateTLD(TL: TokenLogin):
    print("Getting Id With login Progress")
    try:
        login_id = getIdwithLogin(TL.token, [TL.login])
        numbers = [t[1] for t in login_id]
        loginid = numbers[0]
        TLD = TokenLoginId(**TL.model_dump(), login_id=loginid)
        return TLD
    except Exception as e:
        print("Get Id except Occur")
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

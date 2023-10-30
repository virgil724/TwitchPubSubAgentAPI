import docker
import os
from CreateTLD import CreateTLD
from model import TokenLogin, TokenLoginId


client = docker.DockerClient(base_url=os.getenv("DOCKER_SOCK"))


def docker_create(TLD: TokenLoginId):
    try:
        client.containers.run(
            image="twitchsub",
            name=f"TwitchSub_{TLD.login}",
            detach=True,
            labels=["TwitchSub"],
            environment={
                "token": TLD.token,
                "channelId": TLD.login_id,
                "login": TLD.login,
            },
        )

    except Exception as e:
        raise e


def docker_delete(login):
    try:
        container_list = client.containers.list(
            all=True, filters={"name": f"TwitchSub_{login}", "label": "TwitchSub"}
        )
        for container in container_list:
            container.remove(force=True)

    except:
        pass


def docker_update(TL: TokenLogin):
    try:
        docker_delete(TL.login)
        TLD = CreateTLD(TL)
        docker_create(TLD)
    except Exception as e:
        raise e
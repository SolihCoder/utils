import httpx

from core.settings import settings


async def get_check_exists_by_id(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url)
        if response.status_code == 200:
            return response.json()
        else:
            return response.content.decode('utf-8')


async def check_real_estate_exists_by_id(real_estate_id: int):
    url = settings.REALESTATE_SERVICE_URL + settings.API_VERSION + '/real_estates/exists/' + str(real_estate_id)
    result = await get_check_exists_by_id(url)
    return result


async def check_post_exists_by_id(post_id: int):
    url = settings.POST_SERVICE_URL + settings.API_VERSION + '/posts/exists/' + str(post_id)
    result = await get_check_exists_by_id(url)
    return result

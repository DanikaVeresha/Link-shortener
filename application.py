import os

from aiohttp import web
import motor.motor_asyncio


async def index_page(request):
    return web.Response(text="Hello, my project!")


async def redirecter(request):
    resourse_id = request.match_info['resourse_id']
    client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:example@{os.environ.get("DB_HOST","localhost")}localhost:27017')
    db = client['redirecter']
    collection = db['redirects']
    document = await collection.find_one({'resourse_id': resourse_id})
    if document is None:
        return web.Response(text="Not found", status=404)
    long_url = document['long_url']
    return web.HTTPFound(long_url)

app = web.Application()
app.add_routes([web.get('/', index_page)])
app.add_routes([web.get('/{resourse_id}', redirecter)])
web.run_app(app)

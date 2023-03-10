import os
import random
import string
from aiohttp import web
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb://root:example@{os.environ.get("DB_HOST","localhost")}:27017')
db = client['redirecter']
collection = db['redirects']


def html_response(document):
    file = open(document, "r")
    return web.Response(text=file.read(), content_type='text/html')


async def index_page(request):
    return html_response('redirecter.html')


async def recieve_url(request):
    data = await request.post()
    long_url = data['lond_url']
    generate_resourse_id = ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(6))
    document = await collection.insert_one(
        {'long_url': long_url,
         'resourse_id': generate_resourse_id})
    return web.Response(text=generate_resourse_id,
                        content_type='text/plain')


async def redirecter(request):
    resourse_id = request.match_info['resourse_id']
    document = await collection.find_one({'resourse_id': resourse_id})
    if document is None:
        return web.Response(text="Not found", status=404)
    long_url = document['long_url']
    return web.HTTPFound(long_url)

app = web.Application()
app.add_routes([web.get('/', index_page)])
app.add_routes([web.post('/', recieve_url)])
app.add_routes([web.get('/{resourse_id}', redirecter)])
web.run_app(app)






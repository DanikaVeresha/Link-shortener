import os
import random
import string
from aiohttp import web
import motor.motor_asyncio


async def index_page(request):
    return web.Response(text="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Redirecter</title>
</head>
<body>
<h1>Redirecter</h1>
<p>Redirects to a long URL based on a short URL,</p>
<form action="/" method="post">
    <input type="text" name="lond_url" placeholder="Long URL" id="long_url" required>
    <input type="submit" value="Short id">
</form>
</body>
</html>""", content_type='text/html')


async def recieve_url(request):
    data = await request.post()
    long_url = data['lond_url']
    client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:example@{os.environ.get("DB_HOST","localhost")}:27017')
    db = client['redirecter']
    collection = db['redirects']
    generate_resourse_id = ''.join(random.choice(string.ascii_letters + string.digits)for _ in range(6))
    document = await collection.insert_one({'long_url': long_url, 'resourse_id': generate_resourse_id})
    return web.Response(text=generate_resourse_id, content_type='text/plain')


async def redirecter(request):
    resourse_id = request.match_info['resourse_id']
    client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://root:example@{os.environ.get("DB_HOST","localhost")}:27017')
    db = client['redirecter']
    collection = db['redirects']
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

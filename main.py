from aiohttp import web
from handlers import generator_handle

def main():
    app = web.Application()

    routes = [
        ('GET', '/generator', generator_handle, 'generator_handle'),
    ]

    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)

    web.run_app(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()

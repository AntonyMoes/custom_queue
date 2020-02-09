from aiohttp import web
import aiohttp_cors
from handlers import generator_handle, client_handle, stat_handle


def main():
    app = web.Application()

    routes = [
        ('GET', '/generator', generator_handle, 'generator_handle'),
        ('GET', '/client', client_handle, 'client_handle'),
        ('GET', '/stats', stat_handle, 'stat_handle')
    ]

    for method, route, handler, name in routes:
        app.router.add_route(method, route, handler, name=name)

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)

    app['clients'] = dict()
    app['pending'] = dict()
    app['queues'] = dict()
    app['stats'] = {
        'queues': dict(),
        'clients': dict()
    }



    web.run_app(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()


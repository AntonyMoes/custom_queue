from pprint import pprint


def log(app):
    print()
    print('===CLIENTS===')
    pprint(app['clients'])
    print('===QUEUES===')
    pprint(app['queues'])
    print('===PENDING===')
    pprint(app['pending'])
    print()

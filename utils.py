from pprint import pprint
from models import QueueStats
from time import time


def log(app):
    print()
    print('===CLIENTS===')
    pprint(app['clients'])
    print('===QUEUES===')
    pprint(app['queues'])
    print('===PENDING===')
    pprint(app['pending'])
    print('===STATS===')
    pprint(app['stats'])
    print()


def add_stats(app, task, successfull=True):
    if task.id not in app['stats']['queues']:
        app['stats']['queues'][task.id] = QueueStats()

    stats: QueueStats = app['stats']['queues'][task.id]
    if successfull:
        stats.tasks_processed += 1
        stats.sum_live_time += time() - task.time
    stats.sum_process_time += time() - task.started_processing
    stats.sum_process_attempts += 1

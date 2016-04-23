
subscriptions = {}


def subscribe(message, subscriber):
    if message not in subscriptions:
        subscriptions[message] = [subscriber]
    else:
        subscriptions[message].append(subscriber)


def publish(message, *args, **kwargs):
    if message in subscriptions:
        for subscriber in subscriptions[message]:
            try:
                subscriber(*args, **kwargs)
            except Exception:
                pass


def call(obj, method, *args):
    if method in dir(obj):
        try:
            return getattr(obj, method)(*args)
        except AttributeError:
            return False
    else:
        return False

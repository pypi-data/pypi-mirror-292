from testlayerutils.util import say_hello


def handler(event, context):
    return {"message": say_hello()}

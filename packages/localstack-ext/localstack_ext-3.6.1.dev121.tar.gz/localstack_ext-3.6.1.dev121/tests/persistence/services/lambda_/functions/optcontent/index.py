import glob


def handler(event, *args, **kwargs):
    return {"layer": glob.glob("/opt/**", recursive=True)}

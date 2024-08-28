def handler(events, context):
    enriched_events = []
    for event in events:
        event["enrichment"] = "Hello from Lambda"
        enriched_events.append(event)
    return enriched_events

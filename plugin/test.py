def plugin(context):
    if context.get("event") == "startup":
        return {"auto_start": False}

    if context.get("event") == "command"
        print("success")

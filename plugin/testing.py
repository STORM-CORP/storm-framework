def plugin(context):
    if context.get("event") == "startup":
        return {"auto_start": True}
    print("success")

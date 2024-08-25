import inspect


class Argument:
    attr = {"required": True, "type": "attr", "hint": """"""}
    type = {"required": True, "type": "obj", "hint": "type string 30"}
    index = {"type": "prop", "hint": "index true"}
    unique = {"type": "prop", "hint": "unque true"}
    nullable = {"type": "prop", "hint": "nullable false"}
    primary_key = {"type": "prop", "hint": "primary_key true"}
    autoincrement = {"required": False, "type": "prop", "hint": "autoincrement true"}
    args = {"required": False, "type": "obj", "hint": "args ForiegnKey user.id"}

    @staticmethod
    def to_dict():
        return {
            key: value
            for key, value in vars(Argument).items()
            if not key.startswith(("__", "_"))
            and key != "to_dict"
            and not inspect.ismethod(value)
            and not inspect.isfunction(value)
            and not inspect.ismemberdescriptor(value)
        }

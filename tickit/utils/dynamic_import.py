def import_class(target_class: str):
    module_name, class_name = target_class.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)

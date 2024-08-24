import inspect

def get_function_code(function_name):
    # الحصول على كائن الوظيفة من خلال الاسم
    func = globals().get(function_name)
    if func is None:
        return f"No function named {function_name} found."
    
    # الحصول على كود الوظيفة
    source_code = inspect.getsource(func)
    return source_code


def get_class_code(class_name):
    # الحصول على كائن الكلاس من خلال الاسم
    cls = globals().get(class_name)
    if cls is None:
        return f"No class named {class_name} found."
    
    # الحصول على كود الكلاس
    source_code = inspect.getsource(cls)
    return source_code

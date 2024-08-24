from time import sleep
from sys import stdout

    
def print_one(text, second=0.05):
    """This is For Custom Print for Letter

    Args:
        text (str): this is Sentence
        second (float, optional): this is Seconds For Letter. Defaults to 0.05.

    Raises:
        ZeroDivisionError
    """
    
    if len(text) == 0:
        raise ZeroDivisionError
    
    for line in text + '\n':
        stdout.write(line)
        stdout.flush()
        sleep(second)
    

def print_all(text, total_time=5):
    """This is For Custom Print for Sentence

    Args:
        text (_type_): This is Sentence
        total_time (float, optional): This is Seconds For Sentence. Defaults to 5.

    Raises:
        ZeroDivisionError
    """
    
    # حساب الوقت الفاصل بين كل حرف
    if len(text) == 0:
        raise ZeroDivisionError
    else:
        interval = total_time / len(text)
    
    # طباعة النص حرفًا بحرف
    for char in text:
        stdout.write(char)
        stdout.flush()
        sleep(interval)
    
    # طباعة سطر جديد بعد انتهاء النص
    stdout.write('\n')
    stdout.flush()

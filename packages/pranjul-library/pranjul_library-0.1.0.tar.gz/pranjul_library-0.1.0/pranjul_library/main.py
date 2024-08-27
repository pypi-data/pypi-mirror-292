def alternate_string(str1):
    if type(str1) == str:
        return str1[::2]
    else:
        print("It is not string")
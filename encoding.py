import string

def to_base62(num):
    chars = string.digits + string.ascii_letters
    if num == 0:
        return chars[0]
    base62 = []
    while num > 0:
        num, rem = divmod(num, 62)
        base62.append(chars[rem])
    return "".join(reversed(base62))
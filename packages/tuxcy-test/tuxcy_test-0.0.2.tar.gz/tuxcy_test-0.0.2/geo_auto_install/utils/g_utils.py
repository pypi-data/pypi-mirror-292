
def str_to_int(chaine):
    try:
        return int(chaine)
    except ValueError:
        return None
#persistence module




def persistence():
    return False, 'nothing here yet'

def run():
    success, details = persistence()

    if success:
        results = 'Persistence successful, {}.'.format(details)
    else:
        results = 'Persistence unsuccessful, {}.'.format(details)

    return results

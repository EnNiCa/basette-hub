import re

def dni_valido(dni):
    return bool(re.fullmatch(r'[0-9]{8}[A-Za-z]', dni or ''))

def telefono_valido(telefono):
    return bool(re.fullmatch(r'[0-9]{9}', telefono or ''))

def cups_valido(cups):
    if not cups:
        return True  # es opcional, campo vacío es válido
    return bool(re.fullmatch(r'ES[0-9]{16}[A-Za-z]{2}[0-9A-Za-z]{0,4}', cups))

def iban_valido(iban):
    if not iban:
        return True  # es opcional
    limpio = iban.replace(' ', '')
    return bool(re.fullmatch(r'ES[0-9]{22}', limpio))

def cp_valido(cp):
    if not cp:
        return True  # es opcional, campo vacío es válido
    return bool(re.fullmatch(r'[0-9]{5}', cp))
def mask_phone(phone_str):
    """Mask phone number to show only partial digits like +X XXX XXX-XX-XX"""
    if not phone_str or phone_str == "По запросу":
        return phone_str
    
    # Extract only digits
    digits = re.sub(r'\D', '', phone_str)
    
    if len(digits) < 4:
        return "+X XXX XXX-XX-XX"
    
    # Format: +X XXX XXX-XX-XX (show only first digit and last 2 digits)
    if len(digits) >= 11:
        return f"+{digits[0]} XXX XXX-XX-{digits[-2:]}"
    elif len(digits) >= 7:
        return f"+X XXX XXX-XX-{digits[-2:]}"
    else:
        return "+X XXX XXX-XX-XX"

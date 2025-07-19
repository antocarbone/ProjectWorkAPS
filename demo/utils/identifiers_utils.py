def split_UID(full_uid: str):
    uid_parts = full_uid.split(':')
    if len(uid_parts) != 2 or not all(uid_parts):
        raise ValueError("Formato del UID errato.")
    uid = uid_parts[1]
    return uid

def split_CID(full_cid: str):
    cid_parts = full_cid.split(':')
    if len(cid_parts) != 3 or not all(cid_parts):
        raise ValueError("Formato del CID errato.")
    uid = cid_parts[1]
    cid = cid_parts[2]
    return uid, int(cid)

def split_SID(full_sid: str):
    sid_parts = full_sid.split(':')
    if len(sid_parts) != 3 or not all(sid_parts):
        raise ValueError("Formato del SID errato.")
    uid = sid_parts[1]
    sid = sid_parts[2]
    return uid, int(sid)

def assemble_UID(uid: str):
    if not isinstance(uid, str):
        raise ValueError("Il secondo termine dell'UID deve essere una stringa.")
    return 'UID:'+uid

def assemble_CID(uid: str, cid: int):
    if not isinstance(uid, str):
        raise ValueError("Il secondo termine del CID deve essere una stringa.")
    
    if not isinstance(cid, int):
        raise ValueError("Il terzo termine del CID deve essere un intero.")
    
    return 'CID:'+uid+":"+str(cid)

def assemble_SID(uid: str, sid: int):
    if not isinstance(uid, str):
        raise ValueError("Il secondo termine del SID deve essere una stringa.")
    
    if not isinstance(sid, int):
        raise ValueError("Il terzo termine del SID deve essere un intero.")
    
    return 'SID:'+uid+":"+str(sid)
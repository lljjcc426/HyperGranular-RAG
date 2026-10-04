import json

def serialize(payload):
    """One deployment/calibration representation; provenance is not a claim."""
    c=payload['CLAIM'];e=payload['EVIDENCE'];loc=payload['LOCATIONS']
    return ('Claim: "'+c['subject']+'" '+c['relation']+' "'+c['object']+'".\nRequired conditions: '+json.dumps(c['qualifiers'],ensure_ascii=False)+
        '\nSource title: '+e['title']+'\nOriginal evidence:\n'+'\n'.join(s['sid']+': '+s['text'] for s in e['sentences'])+
        '\nMention identities: '+json.dumps({k:dict(mention=loc[k]['text'],identity=loc[k]['identity'],basis=loc[k]['identity_basis']) for k in ('head','tail')},ensure_ascii=False)+
        '\nIs this exact claim, direction and ALL required conditions supported? Answer yes or no.')

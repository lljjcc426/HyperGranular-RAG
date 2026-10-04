def obj(props):return dict(type='object',properties=props,required=list(props),additionalProperties=False)
STR=dict(type='string',minLength=1)
REL=obj(dict(head=STR,relation=STR,tail=STR,qualifiers=dict(type='array',items=STR,maxItems=4)))
PLAN=obj(dict(status=dict(type='string',enum=['ok','ambiguous','unsupported']),relations=dict(type='array',items=REL,maxItems=4)))
MENTION=obj(dict(sid=STR,text=STR,occurrence=dict(type='integer',minimum=0),identity=dict(type='string')))
EXTRACTION=obj(dict(facts=dict(type='array',maxItems=3,items=obj(dict(slot=dict(type='integer',minimum=0,maximum=3),head=MENTION,tail=MENTION,support_sids=dict(type='array',items=STR,minItems=1,maxItems=3),status=dict(type='string',enum=['supported','unresolved']))))))

PARSE_PROMPT='''Translate the QUESTION into ONE JSON OBJECT with status and relations. Never output an array as the top level. Do not answer the question or invent names.
Each relation has head, relation, tail, qualifiers (list of exact question phrases). Use at most four relations. Unknown entities are ?v1, ?v2, ?v3; the requested answer is ALWAYS ?answer. Every non-variable head/tail is copied from QUESTION. Preserve direction and all question constraints. Use variables for unnamed objects, not generic noun phrases as if they were names. Put type/time constraints in qualifiers, not disconnected extra relations. Do not introduce a founder when asked a founding date.
Return status ambiguous if the question cannot identify its referent, unsupported for comparisons/disjunction/negation that require more than positive directed relations. Otherwise status ok. Non-ok may have no relations. Examples are invented and not answers to the user.
Q: When was Atlas Press founded?
{"status":"ok","relations":[{"head":"Atlas Press","relation":"founded on","tail":"?answer","qualifiers":[]}]}
Q: Who is the father of the composer of Silver Lake?
{"status":"ok","relations":[{"head":"Silver Lake","relation":"composed by","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"has father","tail":"?answer","qualifiers":[]}]}
Q: Who published the novel by Mira Reed that was adapted into a film?
{"status":"ok","relations":[{"head":"?v1","relation":"written by","tail":"Mira Reed","qualifiers":["novel","adapted into a film"]},{"head":"?v1","relation":"published by","tail":"?answer","qualifiers":[]}]}
Q: Where was the writer of Night River born?
{"status":"ok","relations":[{"head":"Night River","relation":"written by","tail":"?v1","qualifiers":[]},{"head":"?v1","relation":"born in","tail":"?answer","qualifiers":[]}]}
Q: Which team did the player born in Fairtown join in 2012?
{"status":"ok","relations":[{"head":"?v1","relation":"born in","tail":"Fairtown","qualifiers":["player"]},{"head":"?v1","relation":"joined","tail":"?answer","qualifiers":["in 2012"]}]}
Q: Who founded it?
{"status":"ambiguous","relations":[]}
Do not copy example constants into a different question. Return only the object.'''

EXTRACT_PROMPT='''Locate up to 3 facts supporting the requested relations in this ONE window. Return one object with facts. Do not rewrite quotes. For each fact return slot (zero-based), head and tail mentions {sid,text,occurrence,identity}, support_sids, status. sid refers to sentence IDs s0,s1,s2. text is an EXACT SHORT substring, occurrence is zero-based within that sentence. identity is empty unless resolving a pronoun/alias to an EXACT name in another sentence or the supplied title. Never output ?variables as mentions. support_sids must include every sentence needed for relation, qualifiers and identity. Do not use facts outside this window. Title can identify a subject but cannot prove a relationship without body evidence. Missing/different entity/negated/wrong condition means no supported fact. Use empty facts when nothing supports any requested relation. Other slots need not be satisfied in this window; a variable endpoint may bind to an explicit entity.
Example relation: Green Sky --written by--> ?answer. Body s0: Ada wrote Green Sky.
{"facts":[{"slot":0,"head":{"sid":"s0","text":"Green Sky","occurrence":0,"identity":""},"tail":{"sid":"s0","text":"Ada","occurrence":0,"identity":""},"support_sids":["s0"],"status":"supported"}]}
Do not infer a publication relation just because a writer and a publisher occur in the same window. Preserve has father direction, dates, places and qualifiers. Return JSON only.'''

VERIFY_PROMPT='''Judge whether the supplied EVIDENCE explicitly supports CLAIM with its direction, all qualifiers, and the proposed mention-to-identity links. Use only the shown original sentences and title. Title may resolve a body pronoun but cannot by itself establish a relation. Wrong binding, inverse relation, missing qualifier or insufficient evidence means no. Other question relations need not be satisfied here. Answer exactly yes or no.'''

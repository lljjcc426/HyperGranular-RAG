"""D0 diagnostic plans, reviewed from question text only. Never imported by D1."""
from common import *
def relation(h,r,t,*q):return dict(head=h,relation=r,tail=t,qualifiers=list(q))
R=relation
PLANS=[
 [R('Pericles','became a general of','Athens','after which conflicts between the Achaemenid Empire and Greek city-states'),R('Pericles','became general after','?answer','conflicts between the Achaemenid Empire and Greek city-states')],
 [R('Mehmet Nazif Günal','owns','?v1','100%','cargo airline'),R('?v1','headquartered in','?answer')],
 [R('?v1','re-signed to','Warriors','American retired professional basketball player','during the offseason of  2000–01 NBA'),R('?v1','born on','?answer')],
 [R('Diane Ladd','has daughter','?v1'),R('?v1','performed in','?answer','nominated for the Academy Award for Best Actress')],
 [R('The Bugs Bunny/Road Runner Movie','featured a waterfall based on a work created by','?v1','1979','carrot waterfall'),R('?v1','born on','?answer')],
 [R('ESL Music','founded by','?v1','American heir and hotelier'),R('?v1','died on','?answer')],
 [R('?v1','built by','Raytheon','single-engine turbopop aircraft'),R('?answer','operates','?v1','part of the 47th flying training wing')],
 [R('?v1','written by','Anthony Johnston','graphic novel','a spy thriller film was adapted'),R('?v1','published by','?answer')],
 [R('?v1','located in','Norman','school'),R('?v1','has athletic director','?v2','current'),R('?v2','born in year','?answer')],
 [R('Dale Hamer','was head linesman in','?v1','first Superbowl'),R('?v1','had NFC team','?answer')],
 [R('Frosted','attended','?answer','stake','June 6, 2015','American Thoroughbred racehorse')],
 [R('C. Scott Vanderhoef','was running mate of','?v1','minority leader'),R('?v1','represents','?answer','now','New York district')],
 [R("Pachuca's Monumental Clock",'has identical machinery as','?answer','Great Bell','located at the north end of the Palace of Westminster in London')],
 [R('The Walt Disney Company','acquired','?answer','comic company','has fictional supervillain, that is a foe of the Avengers and the X-Men')],
 [R('Born Free','features','?answer','American singer-songwriter, guitarist and pianist','produced by Rick Rubin')],
 [R('Miss Martian','voiced by','?answer','Young Justice','American actress, mathematics writer, and education advocate'),R('?answer','played','Winnie Cooper','The Wonder Years')],
 [R('Timken High School','located in state','?v1'),R('?v2','held in','?v1','golf tournament in Akron'),R('?v2','held when','?answer')],
 [R('new Magnum PI','filmed in state','?v1'),R('?answer','forming in','?v1','new island')],
 [R('Roses in the Snow','recorded by','?v1'),R('?v1','recorded for','?answer','record label')],
 [R('Crawl','sung by','?v1'),R('Freaky Friday','by','?v1'),R('Freaky Friday','came out on','?answer')],
 [R('Largo','in county','?v1'),R('?v1','has largest city','?answer')],
 [R('?v1','has sole power of','impeachment'),R('?v1','has members elected on','?answer')],
 [R('Layou River','located in country','?v1'),R('?v1','first participated in Olympic games in','?answer')],
 [R('Badsworth','in city','?v1'),R('?v2','named after','?v1','battle'),R('?v2','ended on','?answer')],
 [R('Clinton Derricks-Carroll','born in','?v1'),R('?v1','capital of','?answer','county')],
 [R('Narachen Glacier','located on continent','?v1'),R('?v1','has border latitude','?answer')],
 [R('Piano Sonata No. 17','composed by','?v1'),R('?v1','has father','?answer')],
 None, # "the island" is unidentified in the question; retain ambiguous.
 [R('Comcentre','located in country','?v1'),R('?v1','has majority race','?answer')],
 [R('Jothi Venkatachalam','member of','?v1','political party'),R('?v1','first elected Muslim president','?answer')],
 [R('Llanddeusant','located in','?v1'),R('?answer','established in','?v1','comprehensive school')],
 [R('iPod','produced by','?v1'),R('?v1','produces','OS X'),R('OS X','has latest version named','?answer')],
]
def plans(index):
    rs=PLANS[index]
    return [] if rs is None else [dict(id='r'+str(j+1),**r) for j,r in enumerate(rs)]


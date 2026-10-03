"""Assistant source-reading annotations, fixed before verifier scores; not expert gold."""
from io_utils import *
CLAIMS=[
('Pericles was a general of Athens.','Athens was a general serving Pericles.','Pericles won exactly ten battles.'),
('Mehmet Nazif Günal owns 100% of MNG Airlines.','MNG Airlines owns 100% of Mehmet Nazif Günal.','MNG Airlines is headquartered in Ankara.'),
('Christopher Paul Mullin was born on July 30, 1963.','Christopher Paul Mullin was born on November 24, 2009.','Christopher Paul Mullin was re-signed during the 2000–01 offseason.'),
('Ladd is the mother of Laura Dern.','Laura Dern is the mother of Ladd.','Laura Dern won the Academy Award for Best Actress for Chinatown.'),
('Frank Lloyd Wright was born on June 8, 1867.','Frank Lloyd Wright was born on April 9, 1959.','Frank Lloyd Wright designed the carrot waterfall in The Bugs Bunny/Road Runner Movie.'),
('ESL Music was founded by Rob Garza and Eric Hilton in 1996.','ESL Music founded Rob Garza and Eric Hilton in 1996.','Eric Hilton died on December 10, 2016.'),
('The 85th Flying Training Squadron operates Beechcraft T-6 Texan II aircraft.','Beechcraft T-6 Texan II operates the 85th Flying Training Squadron.','Raytheon built the Beechcraft T-6 Texan II.'),
('The Coldest City was adapted for film as Atomic Blonde.','Atomic Blonde was adapted into the graphic novel The Coldest City.','Oni Press published The Coldest City.'),
('The University of Oklahoma is located in Norman.','Norman is located inside the University of Oklahoma.','The athletic director was born in 1957.'),
('Washington Redskins were the NFC champion in Super Bowl XVII.','Miami Dolphins were the NFC champion in Super Bowl XVII.','Dale Hamer was the head linesman in Super Bowl XVII.'),
('The text mentions a runner-up performance in the 2015 Belmont Stakes.','The text says American Pharoah finished behind the runner-up four times.','The 2015 Belmont Stakes took place on June 6.'),
('John James Faso Jr. represents New York’s 19th congressional district since January 3, 2017.','John James Faso Jr. represents New York’s 102nd congressional district since January 3, 2017.','C. Scott Vanderhoef was John James Faso Jr.’s running mate.'),
('Big Ben is a nickname for the Great Bell at the north end of the Palace of Westminster.','Elizabeth Tower is the official name of the Great Bell.','Pachuca’s Monumental Clock has the same machinery as Big Ben.'),
('Viper appears in comic books published by Marvel Comics.','Viper appears in comic books published by DC Comics.','The Walt Disney Company acquired Marvel Comics.'),
('The album was produced by Rick Rubin and features Sheryl Crow.','The album was produced by Sheryl Crow and features Rick Rubin.','Sheryl Crow is a pianist.'),
('Miss Martian is voiced by Danica McKellar in Young Justice.','Miss Martian is voiced by Sharon Leal in Young Justice.','Danica McKellar played Winnie Cooper.'),
('Timken High School was in Canton, Ohio.','Canton was a high school located in Timken.','The Akron golf tournament takes place in August.'),
('Lōihi Seamount is off the southeast coast of Hawaii.','Hawaii is a submarine volcano off Lōihi Seamount.','The new Magnum PI was filmed in Hawaii.'),
('Roses in the Snow is an album by Emmylou Harris released in 1980.','Blue Kentucky Girl is an album by Emmylou Harris released in 1980.','Emmylou Harris recorded for Reprise Records.'),
('Crawl is a song by Chris Brown.','Graffiti is the second single from the studio album Crawl.','Freaky Friday was released on March 15, 2018.'),
('Pinellas County is in Florida.','Florida is a county in Pinellas County.','St. Petersburg is the largest city in Pinellas County.'),
('Most 2018 United States elections will be held on November 6, 2018.','The text says the federal government administers all 2018 election races.','The House of Representatives has the sole power of impeachment.'),
('The Layou River is in Dominica.','The Layou River is in the Dominican Republic.','Dominica first competed in the Olympic Games in 1996.'),
('Badsworth is in the City of Wakefield metropolitan borough.','Wakefield is a village inside Badsworth parish.','The Battle of Wakefield ended on December 30, 1460.'),
('The Knoxville City-County Building houses Knox County government offices.','Knox County Jail houses the Knoxville City-County Building.','Clinton Derricks-Carroll was born in Knoxville.'),
('Narechen Glacier is on Alexander Island in Antarctica.','Alexander Island is a glacier draining the slopes of Narechen Glacier.','Antarctica’s boundary is latitude 60 degrees south.'),
('Wolfgang Amadeus Mozart was born to Leopold Mozart and Anna Maria.','Leopold Mozart was born to Wolfgang Amadeus Mozart and Anna Maria.','Wolfgang Amadeus Mozart composed Piano Sonata No. 17.'),
('The company received a Royal Charter from Queen Elizabeth I on 31 December 1600.','Queen Elizabeth I received a Royal Charter from the company on 31 December 1600.','The charter gave the company the sole right to fortify the island.'),
('Comcentre is in Singapore.','Singapore is a 32-storey skyscraper in Comcentre.','Chinese people make up the majority of Singapore’s population.'),
('Badruddin Tayyab Ji was the first Muslim president of Indian National Congress.','Rahimtullah M Sayani was the first Muslim president of Indian National Congress.','Jothi Venkatachalam belonged to Indian National Congress.'),
('Llanddeusant is on Anglesey in North Wales.','Anglesey is a village in Llanddeusant parish.','Ysgol Uwchradd Bodedern was the comprehensive school established there.'),
('macOS was developed and marketed by Apple Inc.','Apple Inc. was developed and marketed by macOS.','The latest OS X version was El Capitan.')
]
def main():
    packets=read(LOCAL/'d0_packets.json');assert len(packets)==len(CLAIMS)==32
    out=[]
    for i,triple in enumerate(CLAIMS):
        for j,claim in enumerate(triple):
            out.append(dict(index=i,claim=claim,label=int(j==0),category=('supported','binding_or_direction','missing_information')[j],
                annotation='assistant direct reading of the single displayed body; no external fact lookup',unknown=False))
    save(LOCAL/'annotations.json',out)
    print('96 assistant development annotations; no expert/independence claim')
if __name__=='__main__':main()

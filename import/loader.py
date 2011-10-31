from BeautifulSoup import BeautifulSoup
import pycurl
import StringIO
import re
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

path = BASE_DIR
project = '/ffxivarmoury'
if path not in sys.path:
    sys.path.append(path)
    sys.path.append(path+project)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ffxivarmoury.settings'
from history.models import Character, Event, CharacterEvent

chars = Character.objects.all()
for char in chars:

    # need to add home town aetheryte and starting mission
    if char.nation.name == "Limsa Lominsa":
        ea = Event.objects.get(title="Limsa Lominsa reached!")
        em = Event.objects.get(title="Shapeless Melody complete!")
    elif char.nation.name == "Ul'dah":
        ea = Event.objects.get(title="Ul'dah reached!")
        em = Event.objects.get(title="Flowers for All complete!")
    else:
        ea = Event.objects.get(title="Gridania reached!")
        em = Event.objects.get(title="Sundered Skies complete!")
    CharacterEvent(character=char, event=ea, date_completed='2011-08-12').save()
    CharacterEvent(character=char, event=em, date_completed='2011-08-12').save()

    print "Importing %s (%s)" % (char.name, char.world.name)
    c = pycurl.Curl()
    b = StringIO.StringIO()
    c.setopt(pycurl.URL, "http://lodestone.finalfantasyxiv.com/rc/character/playlog?cicuid=%d&num=100&p=1" % char.cicuid)
    c.setopt(pycurl.HTTPHEADER,["Accept-Language: en-us,en"]) # otherwise we get japanese
    c.setopt(pycurl.WRITEFUNCTION, b.write)
    c.perform()

    html = b.getvalue()

    m = re.search(r'Displaying 1-\d+ of (\d+)', html)
    total = int(m.group(1))
    pages = total / 100 + 1

    for page in xrange(pages):
        print "page %d of %d" % (page+1, pages)

        # SE has fancy double quotes and <wbr/> tags for company missions that mess things up
        html = re.sub(r'...<wbr/>','"',html)
        html = re.sub("&#39;","'",html)

        history = BeautifulSoup(html)


        event_titles = history.findAll('div','contents-headline')
        #event_frames = history.findAll('div','contents-frame')

        # orange -> rank up
        # green -> quest
        # purplishred -> empire?
        # blue -> aetheryte
        # gc[city] -> grand company [city] mission
        # yellow -> faction leves / milestones (number completed, gil reward)
        # red -> enemies defeated milestones
        # gray -> guild mark purchase

        events = {}
        for event in event_titles:
            m = re.search('^ch-(\w+)', event['class'])
            type = m.group(1)
            if type not in events.keys():
                events[type] = []
            events[type].append(event.div.contents[1].div.contents[0])

        for group in events.values():
            for event in group:
                try:
                    event = str(event)
                    if event in ["Hatching-tide reward obtained!","Firefall Faire reward obtained!","All Saints Wake reward obtained!"]:
                        special = re.sub(r'(^.+) obtained!$',r'\1',event)
                        num = char.events.filter(title__startswith=special).count()
                        event = "%s (%d) obtained!" % (special, num + 1)
                    if event == "Observed Hunter's Moon!":
                        special = event[:-1]
                        num = char.events.filter(title__startswith=special).count()
                        event = "%s (%d)!" % (special, num + 1)
                    if event == "Partook in Foundation Day festivities!":
                        special = event[:-1]
                        num = char.events.filter(title__startswith=special).count()
                        event = "%s (%d)!" % (special, num + 1)

                    e = Event.objects.get(title=event)
                    CharacterEvent(character=char, event=e, date_completed='2011-08-12').save()
                except Event.MultipleObjectsReturned:
                    # these are the shared ARM/BSM class quests
                    for e in Event.objects.filter(title=event):
                        CharacterEvent(character=char, event=e, date_completed='2011-08-12').save()
                except Event.DoesNotExist:
                    print "could not find event: %s" % event
        if page + 1 < pages:
            b.truncate(0)
            c.setopt(pycurl.URL, "http://lodestone.finalfantasyxiv.com/rc/character/playlog?cicuid=%d&num=100&p=%d" % (char.cicuid, page+2))
            c.perform()
            html = b.getvalue()
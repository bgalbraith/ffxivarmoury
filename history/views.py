from django.shortcuts import render_to_response
from django.http import Http404
from history.models import Character, Event, EventGroup, Nation, EventType
import re

def index(request):
    chars = Character.objects.all()
    characters = []
    for c in chars:
        characters.append({'id':c.id, 'name':c.name, 'world': c.world.name, 'count':c.events.count()})
    total = Event.objects.count() - 8
    return render_to_response('history/index.html', { 'characters' : characters, 'total' : total })

def events(request, type_name, character_id):
    try:
        type = EventType.objects.get(type=type_name)
        character = Character.objects.get(pk=character_id)
    except EventType.DoesNotExist:
        raise Http404
    except Character.DoesNotExist:
        raise Http404

    groups = type.eventgroup_set.filter(parent=0)
    history = character.events.filter(group__type=type.id)
    count = history.count()
    total = 0
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.all()

        zone = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'count' : s.event_set.count(), 'achieved' : 0, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(" reached!", "", event.title)
                event_class = "event"
                if label[0:4] == 'Camp' or label in ["Limsa Lominsa", "Ul'dah", "Gridania"]:
                    event_class += " camp"
                if event in history:
                    event_class += " achieved"
                    sub['achieved'] += 1
                sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            zone['count'] += sub['count']
            zone['achieved'] += sub['achieved']
            zone['subs'].append(sub)
        events.append(zone)
        total += zone['count']
    return render_to_response('history/aetheryte.html', {
        "events" : events,
        "character" : character,
        "count" : count,
        "total" : total,
        "characters" : Character.objects.all(),
        "types" : EventType.objects.all(),
        "type" : 'aetheryte'})


def aetheryte(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except Character.DoesNotExist:
        raise Http404
    groups = EventGroup.objects.filter(type=1, parent=0)
    history = character.events.filter(group__type=1)
    count = history.count()
    total = 0
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.all()

        zone = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'count' : s.event_set.count(), 'achieved' : 0, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(" reached!", "", event.title)
                event_class = "event"
                if label[0:4] == 'Camp' or label in ["Limsa Lominsa", "Ul'dah", "Gridania"]:
                    event_class += " camp"
                if event in history:
                    event_class += " achieved"
                    sub['achieved'] += 1
                sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            zone['count'] += sub['count']
            zone['achieved'] += sub['achieved']
            zone['subs'].append(sub)
        events.append(zone)
        total += zone['count']
    return render_to_response('history/aetheryte.html', {
        "events" : events,
        "character" : character,
        "count" : count,
        "total" : total,
        "characters" : Character.objects.all(),
        "types" : EventType.objects.all(),
        "type" : 'aetheryte'})

def guild(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except Character.DoesNotExist:
        raise Http404
    groups = EventGroup.objects.filter(type=2, parent=0).exclude(group='General')
    history = character.events.filter(group__type=2)
    count = history.count()
    total = 0
    guilds = []

    ## every guild group (except general) has a rank, quest, and purchase subgroup
    ## general has phys and sentinel ranks and war/magic purchases
    for group in groups:
        guild = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'ranks' : [], 'quests' : [], 'purchases' : []}
        abbr = group.guild.abbreviation.lower()

        try:
            ranks = group.eventgroup_set.get(group__endswith='Ranking')
        except EventGroup.MultipleObjectsReturned:
            pass

        guild['count'] += ranks.event_set.count()
        for event in ranks.event_set.order_by('position').all():
            label = re.sub(' achieved!','',event.title)
            css_class = abbr + '-rank'
            if event in history:
                css_class += '-achieved'
                guild['achieved'] += 1
            guild['ranks'].append({'id' : event.id, 'label' : label, 'css_class' : css_class})

        quests = group.eventgroup_set.get(group__endswith='Quests')
        guild['count'] += quests.event_set.count()
        for event in quests.event_set.order_by('position').all():
            label = re.sub(' complete!','',event.title)
            css_class = 'guild-quest'
            if event in history:
                css_class += '-achieved'
                guild['achieved'] += 1
            guild['quests'].append({'id' : event.id, 'label' : label, 'css_class' : css_class})

        purchases = group.eventgroup_set.get(group__endswith='Purchases')
        guild['count'] += purchases.event_set.count()
        for event in purchases.event_set.order_by('position').all():
            label = re.sub(' acquired!','',event.title)
            css_class = 'guild-purchase'
            if event in history:
                css_class += '-achieved'
                guild['achieved'] += 1
            guild['purchases'].append({'id' : event.id, 'label' : label, 'css_class' : css_class})

        total += guild['count']
        guilds.append(guild)
    return render_to_response('history/guild.html', { "guilds" : guilds, "character" : character, "count" : count, "total" : total })

def quest(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except:
        raise Http404
    nations = Nation.objects.exclude(name=character.nation.name)
    exclude = ["Main Scenario - %s" % n.name for n in nations.all()]
    groups = EventGroup.objects.filter(type=3, parent=0)
    history = character.events.filter(group__type=3)
    count = history.count()
    total = 0
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.exclude(group__in=exclude)

        zone = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'count' : s.event_set.count(), 'achieved' : 0, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(" complete!", "", event.title)
                label = re.sub(r'^.+"(.+)".*$',r'\1',label)
                event_class = "quest-event"
                if event in history:
                    event_class += " achieved"
                    sub['achieved'] += 1
                sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            zone['count'] += sub['count']
            zone['achieved'] += sub['achieved']
            zone['subs'].append(sub)
        events.append(zone)
        total += zone['count']
    return render_to_response('history/quest.html', { "events" : events, "character" : character, "count" : count, "total" : total })
    
def guildleve(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except:
        raise Http404
    groups = EventGroup.objects.filter(type=4, parent=0)
    history = character.events.filter(group__type=4)
    count = history.count()
    total = 0
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.all()

        zone = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'count' : s.event_set.count(), 'achieved' : 0, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(" complete!", "", event.title)
                label = re.sub(r'^(.+) (earned|completed).*$',r'\1',label)
                event_class = "guildleve-event"
                if event in history:
                    event_class += " achieved"
                    sub['achieved'] += 1
                sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            zone['count'] += sub['count']
            zone['achieved'] += sub['achieved']
            zone['subs'].append(sub)
        events.append(zone)
        total += zone['count']
    return render_to_response('history/guildleve.html', { "events" : events, "character" : character, "count" : count, "total" : total })

def combat(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except:
        raise Http404
    groups = EventGroup.objects.filter(type=5, parent=0)
    history = character.events.filter(group__type=5)
    count = history.count()
    total = 0
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.all()

        zone = {'id': group.id, 'name' : group.group, 'count' : 0, 'achieved' : 0, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'count' : s.event_set.count(), 'achieved' : 0, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(" defeated!", "", event.title)
                event_class = "combat-event"
                if event in history:
                    event_class += " achieved"
                    sub['achieved'] += 1
                sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            zone['count'] += sub['count']
            zone['achieved'] += sub['achieved']
            zone['subs'].append(sub)
        events.append(zone)
        total += zone['count']
    return render_to_response('history/combat.html', { "events" : events, "character" : character, "count" : count, "total" : total })

def special(request, characterId):
    try:
        character = Character.objects.get(pk=characterId)
    except:
        raise Http404
    groups = EventGroup.objects.filter(type=6, parent=0)
    history = character.events.filter(group__type=6)
    events = []
    for group in groups:
        subs = [group]
        if group.eventgroup_set.count():
            subs = group.eventgroup_set.all()

        zone = {'id': group.id, 'name' : group.group, 'subs' : []}
        for s in subs:
            sub = {'id' : s.id, 'name' : s.group, 'events' : []}
            for event in s.event_set.order_by('position').all():
                label = re.sub(r" (obtained|complete)!", "", event.title)
                label = re.sub('!','',label)
                event_class = "special-event"
                if event in history:
                    sub['events'].append({'id' : event.id, 'label' : label, 'event_class' : event_class})
            if len(sub['events']):
                zone['subs'].append(sub)
        if len(zone['subs']):
            events.append(zone)
    return render_to_response('history/special.html', { "events" : events, "character" : character })

from django.db import models

class World(models.Model):
    name = models.CharField(max_length=100)

class Region(models.Model):
    name = models.CharField(max_length=100)

class Nation(models.Model):
    name = models.CharField(max_length=100)

class Guild(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3)

class EventType(models.Model):
    type = models.CharField(max_length=100)

class EventGroup(models.Model):
    group = models.CharField(max_length=255)
    type = models.ForeignKey(EventType)
    region = models.ForeignKey(Region, null=True)
    guild = models.ForeignKey(Guild, null=True)
    parent = models.ForeignKey("EventGroup")

class Event(models.Model):
    title = models.CharField(max_length=255)
    group = models.ForeignKey(EventGroup)
    position = models.IntegerField()

class Character(models.Model):
    name = models.CharField(max_length=100)
    world = models.ForeignKey(World)
    nation = models.ForeignKey(Nation)
    cicuid = models.IntegerField()
    events = models.ManyToManyField(Event, through='CharacterEvent')

class CharacterEvent(models.Model):
    character = models.ForeignKey(Character)
    event = models.ForeignKey(Event)
    date_completed = models.DateField()
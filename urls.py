from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^history/$', 'history.views.index'),
    url(r'^history/(?P<type_name>\w+)/(?P<character_id>\d+)$', 'history.views.events')
#    url(r'^history/aetheryte/(?P<characterId>\d+)$', 'history.views.aetheryte'),
#    url(r'^history/guild/(?P<characterId>\d+)$', 'history.views.guild'),
#    url(r'^history/quest/(?P<characterId>\d+)$', 'history.views.quest'),
#    url(r'^history/guildleve/(?P<characterId>\d+)$', 'history.views.guildleve'),
#    url(r'^history/combat/(?P<characterId>\d+)$', 'history.views.combat'),
#    url(r'^history/special/(?P<characterId>\d+)$', 'history.views.special')

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

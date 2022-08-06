from django.contrib import admin
from .models import StreamingPlatform, WatchList, Review

# Register your models here.
admin.site.register(WatchList)
admin.site.register(StreamingPlatform)
admin.site.register(Review)
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Quote)
admin.site.register(Annotation)
admin.site.register(SuggestionComment)
admin.site.register(User)
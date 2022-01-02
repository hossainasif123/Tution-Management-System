from django.contrib import admin
from .models import Ad, Question, Answer, Proposal, Assignee


admin.site.register(Ad)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Proposal)
admin.site.register(Assignee)

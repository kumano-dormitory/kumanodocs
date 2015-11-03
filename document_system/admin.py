from django.contrib import admin
from document_system.models import Meeting, Issue, Note, Block, IssueType, Table

# Register your models here.
admin.site.register(Meeting)
admin.site.register(Issue)
admin.site.register(Note)

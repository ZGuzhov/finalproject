from django.contrib import admin
from polls.models import Poll, Question, QuestionInPoll, Answer


admin.site.site_header = u'Администрирование'
admin.site.index_title = u'Управление опросами'


class AnswerInline(admin.TabularInline):
    model = Answer
    min_num = 4
    max_num = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline,]
    list_filter = ('mode',)
    list_display = ('title', 'mode',)
    ordering = ['title']
    search_fields = ('title',)


class AnswerInPollInline(admin.TabularInline):
    model = QuestionInPoll
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [AnswerInPollInline,]
    list_filter = ('public',)
    list_display = ('title', 'description', 'public')
    ordering = ['title', 'public']
    search_fields = ('title', 'description',)
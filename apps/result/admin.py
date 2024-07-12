from django.contrib import admin
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'current_class', 'subject', 'test_score', 'exam_score', 'total_score', 'grade')
    list_filter = ('session', 'term', 'current_class', 'subject')
    search_fields = ('student__surname', 'student__firstname', 'student__registration_number')
    ordering = ('subject', 'student')

    def total_score(self, obj):
        return obj.test_score + obj.exam_score
    total_score.short_description = 'Total Score'

    def grade(self, obj):
        return obj.grade()
    grade.short_description = 'Grade'

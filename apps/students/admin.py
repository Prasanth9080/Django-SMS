from django.contrib import admin
from .models import Student, StudentBulkUpload

class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'surname', 'firstname', 'other_name', 'gender', 'date_of_birth', 'current_class', 'date_of_admission', 'parent_mobile_number')
    search_fields = ('registration_number', 'surname', 'firstname', 'other_name')
    list_filter = ('gender', 'current_class', 'current_status')
    ordering = ('surname', 'firstname', 'other_name')
    readonly_fields = ('date_of_admission',)

class StudentBulkUploadAdmin(admin.ModelAdmin):
    list_display = ('date_uploaded', 'csv_file')
    readonly_fields = ('date_uploaded',)

admin.site.register(Student, StudentAdmin)
admin.site.register(StudentBulkUpload, StudentBulkUploadAdmin)

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class WarehouseAdminSite(AdminSite):
    # Persian site header, title and index title
    site_header = "سیستم انبارداری آهن"
    site_title = "پنل مدیریت انبار"
    index_title = "خوش آمدید به سیستم انبارداری"
    
    # Custom admin site
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

# Create custom admin site instance
warehouse_admin_site = WarehouseAdminSite(name='warehouse_admin')

# Customize admin site colors and styling
admin.site.site_header = "سیستم انبارداری آهن"
admin.site.site_title = "پنل مدیریت انبار"
admin.site.index_title = "خوش آمدید به سیستم انبارداری"

# Custom admin site configuration
admin.site.enable_nav_sidebar = True
admin.site.site_url = '/'

# Custom admin site messages
admin.site.site_header = "سیستم انبارداری آهن"
admin.site.site_title = "پنل مدیریت انبار"
admin.site.index_title = "خوش آمدید به سیستم انبارداری"

# Custom admin site branding
admin.site.site_header = "سیستم انبارداری آهن"
admin.site.site_title = "پنل مدیریت انبار"
admin.site.index_title = "خوش آمدید به سیستم انبارداری"


# app/routes/admin/views/__init__.py

from .base import MyAdminIndexView, AdminModelView
from .parent_views import ParentAdminView
from .puppy_views import PuppyAdminView
from .site_views import AboutSectionAdminView, AnnouncementBannerAdminView
# === Boostrap 5 views === #
from .home.review_view import ReviewAdminView
from .home.hero_view import HeroSectionAdminView 
from .home.about_view import AboutSectionAdminView 



from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.home, name ="home"),
    path("register/",views.registration_view,name="register"),
    path("logout/", views.logout_view, name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path("login/", views.login_view, name='login'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-success/', views.appointment_success, name='appointment_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('eligibility-quiz/', views.eligibility_quiz, name='eligibility_quiz'),
    path('blood-inventory/', views.blood_inventory_view, name='blood_inventory'),
    path('locations/', views.donation_centers_view, name='locations'),
    path('why_donate', views.why_donate_view, name='why_donate' ),
    path('blood_types', views.blood_types_view, name='blood_types' ),
    path('who_are_we', views.who_are_we_views, name='who_are_we' ),
    path('rewards-board/', views.rewards_board, name='rewards_board'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'blood_bank_app.views.custom_404_view'
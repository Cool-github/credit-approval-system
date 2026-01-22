from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.api.views import (
    RegisterView,
    CheckEligibilityView,
    CreateLoanView,
    ViewLoan,
    ViewLoansByCustomer
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register", RegisterView.as_view()),
    path("check-eligibility", CheckEligibilityView.as_view()),
    path("create-loan", CreateLoanView.as_view()),
    path("view-loan/<int:loan_id>", ViewLoan.as_view()),
    path("view-loans/<int:customer_id>", ViewLoansByCustomer.as_view()),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]

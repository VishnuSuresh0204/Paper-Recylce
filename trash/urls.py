"""
URL configuration for trash project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from proApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('userhome/', views.userhome),
    path('contact/', views.contact),
    path('userreg/', views.userreg),
    path('organizerreg/', views.organizerreg),
    path('login/', views.login),
    path('orghome/', views.orghome,name='orghome'),
    path('adminhome/', views.adminhome),
    path('vieworg/', views.vieworg),
    path('accept/', views.accept),
    path('reject/', views.reject),
    path('submitrequest/', views.submitrequest),
    path('requestdetails/', views.requestdetails,name='requestdetails'),
    path('acceptwaste/', views.acceptwaste),
    path('rejectwaste/', views.rejectwaste),
    path('wepicked/', views.wepicked),
    path('userrequestdetails/', views.userrequestdetails),
    path('addproduct/', views.addproduct),
    path('productlist/', views.productlist),
    path('userproductlist/', views.userproductlist),
    path('deleteimg/', views.deleteimg),
    path('buy/', views.buy),
    path('payment/', views.payment),
    path('userorderdetails/', views.userorderdetails),
    path('orderdetailsorg/', views.orderdetailsorg),
    path('shipped/', views.shipped),
    path('delivered/', views.delivered),
    path('productreview/', views.productreview),
    path('adminorderlist/', views.adminorderlist),
    path('adminfeedbacklist/', views.adminfeedbacklist),
    path('adminproductlist/', views.adminproductlist),
    path('orgreviewlist/', views.orgreviewlist),
    path('collectorreg/', views.collectorreg),
    path('collecthome/', views.collecthome,name='collecthome'),
    path('coll_requestdetails/', views.coll_requestdetails,name='coll_requestdetails'),
    path('coll_accept/', views.coll_accept),
    path('acceptwaste_col/', views.acceptwaste_col),
    path('rejectwaste_col/', views.rejectwaste_col),
    # path('wepicked_ad/', views.wepicked_ad),
    path('rejectwaste_adq/', views.rejectwaste_adq),
    path('delete/', views.delete),
    path('approvepaper/', views.approvepaper),
    path('ad/', views.ad),
    path('editproduct/', views.editproduct, name='editproduct'),

    path('userview/', views.user_view, name='user_view'),
    
    path('collector_view/', views.collector_view, name='collector_view'),
    path('accept_collector/<int:id>/', views.accept_collector, name='accept_collector'),
    path('reject_collector/<int:id>/', views.reject_collector, name='reject_collector'),
    path("update_pickup_date/<int:request_id>/", views.update_pickup_date, name="update_pickup_date"),
    path("paper_collection_requests/", views.paper_collection_requests),
    path("assign-organizer/<int:request_id>/", views.assign_to_organizer, name="assign_to_organizer"),
    path('reply/<int:id>/', views.reply, name='reply'),

    path('collector_replies', views.collector_replies, name='collector_replies'),
    path('pay_collector/', views.pay_collector, name='pay_collector'),
    path('assign_collector/', views.assign_collector, name='assign_collector'),
    path('mark_reached/', views.mark_reached, name='mark_reached'),
    path('userpay/', views.userpay, name='userpay'),
    path('add_request_feedback/<int:request_id>/', views.add_request_feedback, name='add_request_feedback'),
    path('edit_request_feedback/<int:feedback_id>/', views.edit_request_feedback, name='edit_request_feedback'),
    path('delete_request_feedback/<int:feedback_id>/', views.delete_request_feedback, name='delete_request_feedback'),
    path('view_feedback/', views.user_view_feedback, name='user_view_feedback'),
    path('edit_request/<int:request_id>/', views.edit_request, name='edit_request'),
    path('add_order_feedback/<int:order_id>/', views.add_order_feedback, name='add_order_feedback'),
    path('edit_order_feedback/<int:feedback_id>/', views.edit_order_feedback, name='edit_order_feedback'),
    path('delete_order_feedback/<int:feedback_id>/', views.delete_order_feedback, name='delete_order_feedback'),
    path('admin_delete_request_feedback/<int:id>/', views.admin_delete_request_feedback, name='admin_delete_request_feedback'),
    path('admin_delete_order_feedback/<int:id>/', views.admin_delete_order_feedback, name='admin_delete_order_feedback'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






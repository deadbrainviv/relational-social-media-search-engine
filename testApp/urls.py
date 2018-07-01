from django.conf.urls import url
from . import views

app_name = 'testApp'
urlpatterns = [
    url(r'^socialgraph/$', views.socialgraph, name='socialgraph'),
	url(r'^inputgroundtruth/$', views.inputgroundtruth, name='inputgroundtruth'),
	url(r'^improvedsocialgraph/$', views.improvedsocialgraph, name='improvedsocialgraph'),
	url(r'^facialrecognition/$', views.facialrecognition, name='facialrecognition'),
    url(r'^lists/$', views.lists, name='lists'),
	]

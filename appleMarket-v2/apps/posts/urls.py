from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
# 기존: path('', main, name='main'),  <-- 아마 이렇게 되어 있을 겁니다.
    # 수정: name='main'을 name='list'로 변경해주세요.
    path('', main, name='list'), 
    
    path('create/', create, name='create'),
    path('detail/<int:pk>/', detail, name='detail'),
    path('update/<int:pk>/', update, name='update'),
    path('delete/<int:pk>/', delete, name='delete'),
    path('api/ocr/', nutrition_ocr_api, name='nutrition_ocr_api'),
    path('api/tagging/', product_tagging_api, name='product_tagging_api'), # 추가
]
# apps/posts/views.py

from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings  # [추가] settings 임포트 필수! (맨 아래 API에서 씀)
import os

# 서비스들 임포트
from .services.ocr_service import get_ocr_result
from .services.rules import parse_nutrition_info
from .services.yolo_service import get_image_tags

# Create your views here.
def main(request):
    # 최신순 정렬을 위해 order_by('-pk') 추가 (선택사항이지만 추천)
    posts = Post.objects.all().order_by('-pk')

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # [추가] 해시태그 검색 파라미터 받기
    hashtag = request.GET.get('hashtag')

    # 1. 제목 검색 필터
    if search_txt:
        posts = posts.filter(title__icontains=search_txt)
    
    # [추가] 2. 해시태그 검색 필터
    if hashtag:
        # hashtags 필드에 해당 단어가 포함되어 있는지 확인 (icontains)
        posts = posts.filter(hashtags__icontains=hashtag)

    # 3. 가격 필터
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
        'hashtag': hashtag, # [추가] 템플릿에서 현재 검색된 태그를 알 수 있게 전달
    }
    return render(request, 'posts/list.html', context=context)

def create(request):
    if request.method == 'GET':
        form = PostForm()
        context = { 'form': form }
        return render(request, 'posts/create.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('/')

def detail(request, pk):
    target_post = Post.objects.get(id = pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form, 
            'post': post
        }
        return render(request, 'posts/update.html', context=context)
    else:
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
        return redirect('posts:detail', pk=pk)

def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

@csrf_exempt
def nutrition_ocr_api(request):
    """
    영양성분 OCR API
    """
    if request.method == 'POST' and request.FILES.get('ocr_image'):
        image = request.FILES['ocr_image']
        
        path = default_storage.save('temp/' + image.name, image)
        full_path = os.path.join(default_storage.location, path)

        try:
            extracted_text = get_ocr_result(full_path)
            nutrition_data = parse_nutrition_info(extracted_text)
            
            return JsonResponse({
                'status': 'success',
                'data': nutrition_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)

    return JsonResponse({'status': 'fail', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def product_tagging_api(request):
    """
    상품 이미지 태깅 API (YOLO)
    """
    if request.method == 'POST' and request.FILES.get('product_image'):
        try:
            image_file = request.FILES['product_image']
            
            # [수정] settings.MEDIA_ROOT를 쓰려면 상단에 import 필요
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', image_file.name)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            
            with open(temp_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)
            
            tags = get_image_tags(temp_path)
            tag_string = ", ".join(tags)

            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return JsonResponse({'status': 'success', 'tags': tag_string})
            
        except Exception as e:
            # 디버깅을 위해 에러 메시지 출력
            print(f"Error in tagging api: {e}")
            return JsonResponse({'status': 'fail', 'message': str(e)})
            
    return JsonResponse({'status': 'fail', 'message': '이미지가 없습니다.'})
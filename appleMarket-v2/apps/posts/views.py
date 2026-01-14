from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os

# 이전에 만든 서비스들 임포트
from .services.ocr_service import get_ocr_result
from .services.rules import parse_nutrition_info

# Create your views here.
def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)  # 대소문자 구분 없이 검색
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass  # 필터를 무시하되, 기존 검색 필터를 유지

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
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
    프론트엔드에서 보낸 이미지를 받아 OCR 처리 후 영양성분 데이터를 JSON으로 반환
    """
    if request.method == 'POST' and request.FILES.get('ocr_image'):
        image = request.FILES['ocr_image']
        
        # 1. 임시 파일 저장
        path = default_storage.save('temp/' + image.name, image)
        full_path = os.path.join(default_storage.location, path)

        try:
            # 2. OCR 실행 (텍스트 추출)
            extracted_text = get_ocr_result(full_path)
            
            # 3. 텍스트 파싱 (데이터 규격화)
            nutrition_data = parse_nutrition_info(extracted_text)
            
            return JsonResponse({
                'status': 'success',
                'data': nutrition_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            # 4. 사용한 임시 파일 삭제 (건설적인 자원 관리)
            if os.path.exists(full_path):
                os.remove(full_path)

    return JsonResponse({'status': 'fail', 'message': 'Invalid request'}, status=400)
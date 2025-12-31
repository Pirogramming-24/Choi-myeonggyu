from django.shortcuts import render, redirect, get_object_or_404
from .models import Review
from .forms import ReviewForm

# Create your views here.
def main(request):
    return render(request, "main.html")

# 기능 1: 리뷰 리스트
def review_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'review_list.html', {'reviews': reviews})

# 기능 4: 리뷰 디테일
def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'review_detail.html', {'review': review})

# reviews/views.py

# 기능 8 & 10: 리뷰 작성
def review_create(request):
    if request.method == "POST":
        # 수정 전: form = ReviewForm(request.POST) 
        # 수정 후: request.FILES를 반드시 추가해야 합니다!
        form = ReviewForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form, 'action': '작성'})

# 기능 9 & 11: 리뷰 수정
def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        # 여기도 마찬가지로 request.FILES 추가!
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_detail', pk=review.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'review_form.html', {'form': form, 'action': '수정'})

# 기능 7: 리뷰 삭제
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
        return redirect('review_list')
    return redirect('review_detail', pk=pk) # POST 요청이 아니면 다시 디테일로
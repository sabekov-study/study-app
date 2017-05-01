from django.shortcuts import render


def test_page(request):
    return render(request, 'base/test_page.html')


def imprint(request):
    return render(request, 'base/imprint.html')

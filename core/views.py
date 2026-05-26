from django.http      import JsonResponse, Http404
from django.shortcuts import render

FRONTEND_PAGES = {
    'index.html', 'login.html', 'restaurants.html',
    'menu.html',  'item.html',  'cart.html', 'orders.html', 'recommendations.html',
    'payment.html', 'payment-success.html', 'addresses.html',
}

def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'BiteRight Backend'})

def frontend_root(request):
    return render(request, 'login.html')

def frontend_page(request, page):
    if page not in FRONTEND_PAGES:
        raise Http404('Page not found')
    return render(request, page)

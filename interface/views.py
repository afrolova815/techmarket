from django.http import HttpResponseNotFound
from django.shortcuts import render


def resource_not_found(request, exception):
    return HttpResponseNotFound(
        "<h1>Ресурс не найден</h1>"
        "<p>Запрошенная страница отсутствует в системе.</p>"
        "<p>Рекомендуем посетить <a href=\"/catalog/\">каталог товаров</a>.</p>"
    )

def main_dashboard(request):
    return render(request, "interface/index.html")

# def main_dashboard(request):
#     return redirect("product_list")

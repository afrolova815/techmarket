from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AddRecordForm, UploadFileForm
from django.conf import settings
import os
import uuid
import datetime


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

def add_record(request):
    if request.method == "POST":
        form = AddRecordForm(request.POST)
        if form.is_valid():
            messages.success(request, "Данные успешно отправлены")
            return redirect("add_record")
        else:
            messages.error(request, "Произошла ошибка. Проверьте правильность заполнения формы.")
    else:
        form = AddRecordForm()
    return render(request, "interface/add_record.html", {"form": form})

def _handle_uploaded_file(fobj):
    base_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(fobj.name)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(base_dir, unique_name)
    with open(full_path, "wb") as dest:
        for chunk in fobj.chunks():
            dest.write(chunk)
    return unique_name

def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file"]
            saved_name = _handle_uploaded_file(f)
            messages.success(request, f"Файл загружен: {saved_name}")
            return redirect("upload_file")
        else:
            messages.error(request, "Ошибка: проверьте корректность файла")
    else:
        form = UploadFileForm()
    return render(request, "interface/upload.html", {"form": form, "title": "Загрузка файла"})

def uploaded_files_list(request):
    base_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    files = []
    if os.path.isdir(base_dir):
        for entry in os.scandir(base_dir):
            if entry.is_file():
                stat = entry.stat()
                files.append({
                    "name": entry.name,
                    "url": f"{settings.MEDIA_URL}uploads/{entry.name}",
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime),
                })
    files.sort(key=lambda x: x["modified"], reverse=True)
    return render(request, "interface/upload_list.html", {"files": files, "title": "Загруженные файлы"})

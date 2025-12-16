from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AddRecordForm, UploadFileForm
from django.conf import settings
import os
import uuid
import datetime
from django.views.generic import TemplateView, FormView, ListView


def resource_not_found(request, exception):
    return HttpResponseNotFound(
        "<h1>Ресурс не найден</h1>"
        "<p>Запрошенная страница отсутствует в системе.</p>"
        "<p>Рекомендуем посетить <a href=\"/catalog/\">каталог товаров</a>.</p>"
    )

class MainDashboardView(TemplateView):
    template_name = "interface/index.html"

class AddRecordView(FormView):
    template_name = "interface/add_record.html"
    form_class = AddRecordForm

    def form_valid(self, form):
        messages.success(self.request, "Данные успешно отправлены")
        return redirect("add_record")

    def form_invalid(self, form):
        messages.error(self.request, "Произошла ошибка. Проверьте правильность заполнения формы.")
        return render(self.request, self.template_name, {"form": form})

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

class UploadFileView(FormView):
    template_name = "interface/upload.html"
    form_class = UploadFileForm

    def form_valid(self, form):
        f = form.cleaned_data["file"]
        saved_name = _handle_uploaded_file(f)
        messages.success(self.request, f"Файл загружен: {saved_name}")
        return redirect("upload_file")

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка: проверьте корректность файла")
        return render(self.request, self.template_name, {"form": form, "title": "Загрузка файла"})

class UploadedFilesListView(ListView):
    template_name = "interface/upload_list.html"
    context_object_name = "files"

    def get_queryset(self):
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
        return files

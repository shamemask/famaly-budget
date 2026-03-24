import logging

from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import URLPattern, path

from monetary_parser.strategems.parser import ParserStrategy

from .forms import TransactionFileUploadForm
from .models import Client, Product, Transaction

logger = logging.getLogger(__name__)


class TransactionAdmin(admin.ModelAdmin):
    change_list_template = "admin/transactions_upload.html"
    list_display = [
        field.name
        for field in Transaction._meta.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload/",
                self.admin_site.admin_view(self.upload_file),
                name="transactions-upload",
            ),
        ]
        return custom_urls + urls

    def upload_file(self, request: HttpRequest) -> HttpResponse:
        if request.method == "POST":
            form = TransactionFileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                file.seek(0)
                file_content = file.read()
                if not file_content:
                    logger.error("Загруженный файл пуст.")
                    self.message_user(request, "Ошибка: Загруженный файл пуст.", level="error")
                    return HttpResponseRedirect("../")

                parser = ParserStrategy(file_content)
                parser.start()
                self.message_user(request, "PDF-файл успешно загружен и обработан.")
                return HttpResponseRedirect("../")
        else:
            form = TransactionFileUploadForm()

        context = {
            "form": form,
            "title": "Загрузка PDF-файла транзакций",
            "app_label": self.model._meta.app_label,
            "opts": self.model._meta,
        }
        return render(request, "admin/upload_file.html", context)


admin.site.register(Client)
admin.site.register(Product)
admin.site.register(Transaction, TransactionAdmin)

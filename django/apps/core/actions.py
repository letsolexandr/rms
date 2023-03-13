
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.utils import lookup_field
from django.utils.html import strip_tags
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date

import xlsxwriter




class ExportExcelAction:
    @classmethod
    def generate_header(cls, admin, model, list_display):
        def default_format(value):
            return value.replace('_', ' ').upper()

        header = []
        for field_display in list_display:
            is_model_field = field_display in [f.name for f in model._meta.fields]
            is_admin_field = hasattr(admin, field_display)
            if is_model_field:
                field = model._meta.get_field(field_display)
                field_name = getattr(field, 'verbose_name', field_display)
                header.append(default_format(field_name))
            elif is_admin_field:
                field = getattr(admin, field_display)
                field_name = getattr(field, 'short_description', default_format(field_display))
                header.append(default_format(field_name))
            else:
                header.append(default_format(field_display))
        return header



def convert_data_date(value):
    return value.strftime('%d/%m/%Y')


def convert_boolean_field(value):
    if value:
        return 'Так'
    return 'Ні'


def export_as_xls(self, request, queryset):
    opts = self.model._meta
    field_names = self.get_list_display(request)
    file_name = opts.verbose_name
    path  = f'/tmp/{timezone.localtime()}.xlsx'

    wb = xlsxwriter.Workbook(path)
    ws = wb.add_worksheet()
    header_format = wb.add_format({'text_wrap': 1, 'valign': 'top',    'bold': 1,
                                       'border': 1,
                                       'align': 'center',
                                       'valign': 'vcenter', })
    rown = 1
    header = ExportExcelAction.generate_header(self, self.model, field_names)
    ws.write_row(f'A{rown}',header,cell_format=header_format)
    ws.set_column('A:BE', 30, cell_format=header_format)

    rown = 2
    for obj in queryset:
        row = []
        for field in field_names:
            
            is_admin_field = hasattr(self, field)
            if is_admin_field:
                value = getattr(self, field)(obj)
            else:
                model_field = opts.get_field(field)
                value = getattr(obj, field)
                if isinstance(value, datetime) or isinstance(value, date):
                    value = convert_data_date(value)
                elif isinstance(value, bool):
                    value = convert_boolean_field(value)
                elif hasattr(model_field,'choices') and getattr(model_field, 'choices'):
                    value = getattr(obj, f'get_{field}_display')()

            row.append(str(value))
        ws.write_row(f'A{rown}',row)
        rown += 1
    wb.close()

    with open(path,'rb') as output:
            response = HttpResponse(output.read())
            response['Content-Disposition'] = f"attachment; filename={timezone.localtime()}.xlsx"
            return response


export_as_xls.short_description = "Експорт в excel"
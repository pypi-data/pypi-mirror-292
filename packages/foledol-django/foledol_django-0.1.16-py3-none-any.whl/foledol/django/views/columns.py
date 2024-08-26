from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from foledol.django.tools.table import TableColumn, TableView

from ..models import Column


class ColumnTable(TableView):
    def __init__(self):
        super().__init__(Column, [
            TableColumn('label', "Libellé")
        ], path='django/columns', search=True)
        self.update = 'django:column_update'
        self.create = 'django:column_create'

    def select(self, columns, search, order_by):
        return columns.filter(label=search) if len(search) > 0 else columns


@login_required
def column_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    return ColumnTable().render(request)

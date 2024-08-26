from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from foledol.django.tools.table import TableColumn, TableView

from ..models import Condition


class ConditionTables(TableView):
    def __init__(self):
        super().__init__(Condition, [
            TableColumn('label', "Libellé"),
            TableColumn('criteria', "Critère"),
            TableColumn('value', "Valeur")
        ], path='django/conditions', search=True)
        self.update = 'django:condition_update'
        self.create = 'django:condition_create'

    def select(self, conditions, search, order_by):
        return conditions.filter(label=search) if len(search) > 0 else conditions


@login_required
def condition_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    return ConditionTables().render(request)

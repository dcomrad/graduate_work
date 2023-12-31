import math
from unittest import mock

from django.contrib.admin.views.main import ChangeList
from django.core.paginator import Paginator


def get_elided_page_range(self, number=1, *, on_each_side=3, on_ends=2):
    if self.num_pages <= (on_each_side + on_ends) * 2:
        yield from range(1, self.num_pages + 1)
        return

    if number > (1 + on_each_side + on_ends) + 1:
        yield from range(1, on_ends + 1)
        yield Paginator.ELLIPSIS
        yield from range(number - on_each_side, number + 1)
    else:
        yield from range(1, number + 1)

    if number < (self.num_pages - on_each_side - on_ends) - 1:
        yield from range(number + 1, number + on_each_side + 1)
        yield Paginator.ELLIPSIS
        yield from range(self.num_pages - on_ends + 1, self.num_pages + 1)
    else:
        yield from range(number + 1, self.num_pages + 1)


class CustomChangeList(ChangeList):
    def get_queryset(self, request):
        parts = self.get_filters(request)
        (self.filter_specs, self.has_filters) = parts[:2]
        return self.root_queryset

    def get_results(self, request):
        result = self.model_admin.get_list(
            request, self.page_num, self.list_per_page
        )
        items = result.get("items") or []

        total = result.get("total") or len(items)

        paginator = mock.MagicMock()
        paginator.count = total
        paginator.num_pages = int(math.ceil(total / self.list_per_page))
        paginator.get_elided_page_range = (
            lambda *args, **kwargs: get_elided_page_range(
                paginator, *args, **kwargs
            )
        )

        self.result_count = paginator.count
        self.show_full_result_count = False
        self.show_admin_actions = True
        self.full_result_count = paginator.count
        self.result_list = items
        self.can_show_all = False
        self.multi_page = True
        self.paginator = paginator

# Third Party Stuff
from django.contrib import messages

# Spoken Tutorial Stuff
from creation.models import *


class SortableHeader():
    def __init__(self, name, sortable, verbose_name='', class_name='', attribs=''):
        self.name = name
        self.sortable = sortable
        self.verbose_name = verbose_name
        self.ordering = ''
        self.removable = ''
        self.class_name = class_name
        self.sort_type = ''
        self.order = 0
        self.attribs = attribs


def get_field_index(raw_get_data):
    if raw_get_data:
        field_index = []
        tmp_index = raw_get_data.split('.')
        for index in tmp_index:
            field_index.append(int(index))
        if field_index:
            return field_index
    return None


def get_sorted_list(request, obj, fields_list, raw_get_data):
    field_index = get_field_index(raw_get_data)
    sort_order = []
    if field_index:
        for index in field_index:
            try:
                fixed_index = index
                if index < 0:
                    fixed_index = index * -1
                field = fields_list[fixed_index]
                if field.sortable:
                    if index < 0:
                        sort_order.append('-' + field.name)
                    else:
                        sort_order.append(field.name)
            except:
                messages.error(request, 'Invalid ordering key has passed!')
                return obj
    if len(sort_order):
        try:
            print sort_order
            return obj.order_by(*sort_order)
        except:
            messages.error(request, 'Invalid field name passed for sorting!')
    return obj


def get_ordering(ordering, unsigned_index, signed_index, sign_to_add):
    order_string = ''
    flag = 1
    removable = ''
    if ordering:
        for order in ordering:
            if order == signed_index:
                if order_string:
                    order_string = str(order * -1) + '.' + order_string
                else:
                    order_string = str(order * -1)
                flag = 0
            else:
                if order_string:
                    order_string = order_string + '.'
                order_string = order_string + str(order)
                if removable:
                    removable = removable + '.'
                removable = removable + str(order)
    if flag:
        if order_string:
            order_string = '.' + order_string
        order_string = sign_to_add + str(unsigned_index) + order_string
        removable = None
    return order_string, removable


def get_sortable_header(header, ordering, getValue):
    descending_list = []
    ascending_list = []
    if ordering:
        counter = 1
        for order in ordering:
            if order < 0:
                header[order * -1].order = counter
                descending_list.append(header[order * -1].name)
            else:
                header[order].order = counter
                ascending_list.append(header[order].name)
            counter = counter + 1
    l = len(header) + 1
    headers = []
    for row in range(l):
        if row == 0:
            continue
        class_name = 'col-' + header[row].name
        signed_index = row
        if header[row].sortable:
            class_name = class_name + ' sortable'
            sign_str = ''
            if header[row].name in ascending_list:
                sign_str = '-'
                class_name = 'sorted ascending ' + class_name
                header[row].sort_type = 'ascending'
            elif header[row].name in descending_list:
                class_name = 'sorted descending ' + class_name
                header[row].sort_type = 'descending'
                signed_index = signed_index * -1
            header[row].ordering, header[row].removable = get_ordering(ordering, row, signed_index, sign_str)
            header[row].class_name = header[row].class_name + ' ' + class_name
        headers.append(header[row])
    context = {
        'headers': headers,
        'getValue': getValue
    }
    return context

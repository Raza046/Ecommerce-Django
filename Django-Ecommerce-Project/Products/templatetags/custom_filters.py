from django import template

register = template.Library()

@register.filter
def unique(value):
    print(value)
    arr = []
    product_list = []
    for i in value:
        if i.color not in arr:
            print(i.color)
            arr.append(i.color)
            product_list.append(i)
    return product_list

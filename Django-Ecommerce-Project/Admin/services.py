from datetime import datetime
from Products.models import ProductVariant, VariationValue


def top_products(product_variants):
    top_poducts = {}
    prod_sold = 0

    for product_variant in product_variants:
        p_variation = ProductVariant.objects.get(id=product_variant['product_variant'])
        top_poducts[p_variation] = product_variant['product_quantity']
        prod_sold += int(product_variant['product_quantity'])
    return top_poducts,prod_sold

def set_product_variaiton(prod_val, p_var):

    product_variation_values = prod_val.split(",")
    for values in product_variation_values:
        variation_id = values.split("__")[0]
        variation_val = values.split("__")[1]
        v_value = VariationValue.objects.get(variation_id=variation_id,value=variation_val)
        p_var.variation.add(v_value)

def GraphFilteration(sales_data):

    month_dict = {
        'January':"0", 'February':"0", 'March':"0", 'April':"0", 'May':"0",
        'June':"0", 'July':"0", 'August':"0", 'September':"0", 'October':"0",
        'November':"0", 'December':"0"
        }

    for data in sales_data:
        month = datetime.strptime(str(data.created_at), '%Y-%m-%d').strftime('%B')
        if month_dict.get(month):
            month_dict[month] = int(month_dict[month]) + 1
    return month_dict

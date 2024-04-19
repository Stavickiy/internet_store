from vitamins.models import Brand


def get_vitamin_context(request):
    brands = Brand.objects.distinct()
    return {'brands': brands}

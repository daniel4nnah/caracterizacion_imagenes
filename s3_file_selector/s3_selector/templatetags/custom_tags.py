from django import template

register = template.Library()

@register.filter
def metadata_to_list(metadata):
    # metadata = metadata_dict.get(post, {})
    return [{'key': key, 'value': value} for key, value in metadata.items()]

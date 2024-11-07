from django import template

register = template.Library()

@register.filter
def get_item(sequence, position):
    """
    Devuelve el elemento en la posición 'position' de 'sequence'.
    """
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return ''


@register.filter
def to_list(start, end):
    """
    Devuelve una lista de números desde 'start' hasta 'end' inclusive.
    """
    return list(range(start, end + 1))

# Dentro do arquivo: app/templatetags/app_tags.py

from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    """
    Este filtro multiplica o 'value' pelo 'arg'
    Uso no HTML: {{ algum_numero|mul:outro_numero }}
    """
    try:
        # Tenta multiplicar como números inteiros
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try:
            # Se não der, tenta como números decimais
            return float(value) * float(arg)
        except (ValueError, TypeError):
            # Se der erro, não quebra o site
            return ''
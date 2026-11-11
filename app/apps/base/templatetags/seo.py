import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def jsonld(data):
    """Безопасно выводит dict как JSON-LD (экранируя </script>)."""
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return mark_safe(raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))


class CaptureNode(template.Node):
    def __init__(self, nodelist, var):
        self.nodelist, self.var = nodelist, var

    def render(self, context):
        context[self.var] = ' '.join(self.nodelist.render(context).split())
        return ''


@register.tag
def capture(parser, token):
    """{% capture as page_title %}...{% endcapture %} — рендерит блок в переменную."""
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise template.TemplateSyntaxError('Использование: {% capture as имя %}...{% endcapture %}')
    nodelist = parser.parse(('endcapture',))
    parser.delete_first_token()
    return CaptureNode(nodelist, bits[2])


@register.simple_tag
def breadcrumbs_jsonld(crumbs):
    from apps.base.seo import breadcrumbs_schema
    return jsonld(breadcrumbs_schema(crumbs))


@register.filter
def split_pipe(value):
    """'a|b|c' -> ['a', 'b', 'c']"""
    return [v.strip() for v in str(value).split('|') if v.strip()]

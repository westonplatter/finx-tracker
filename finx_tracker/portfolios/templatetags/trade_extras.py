from django import template

register = template.Library()


def render_grouping_names(groupings):
    return ", ".join(grouping.name for grouping in groupings.all())


register.filter("render_grouping_names", render_grouping_names)

from django import template

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

@register.filter(name='to_int') 
def to_int(value):
    try:
        return int(value)
    except :
        return False
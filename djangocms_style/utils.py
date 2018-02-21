from cms.models import CMSPlugin
from aldryn_style.models import Style
from djangocms_style.models import Style as DStyle
from cms.utils.plugins import copy_plugins_to_placeholder

'''
First edit djangocms_style.cms_plugins and set StylePlugin.name = _('Style_DjangoCMS')

Then set StylePlugin.__name__ = 'DjangoCMSStylePlugin'
before registering plugin.
Change these back to 'Style' and 'StylePlugin' once plugins have been migrated.
'''

def migrateStyle(old_plugin):
    old_plugin = old_plugin.get_bound_plugin()
    children = old_plugin.get_children()
    
    new_plugin = DStyle(
        language = old_plugin.language,
        parent = old_plugin.parent,
        placeholder = old_plugin.placeholder,
        position = old_plugin.position,
        plugin_type = 'DjangoCMSStylePlugin',

        label = old_plugin.label,
        class_name = old_plugin.class_name,
        id_name = old_plugin.id_name,
        tag_type = old_plugin.tag_type,
        additional_classes = old_plugin.additional_class_names,
        padding_top = old_plugin.padding_top,
        padding_right = old_plugin.padding_right,
        padding_bottom = old_plugin.padding_bottom,
        padding_left = old_plugin.padding_left,
        margin_top = old_plugin.margin_top,
        margin_right = old_plugin.margin_right,
        margin_bottom = old_plugin.margin_bottom,
        margin_left = old_plugin.margin_left,
    )

    # insert new plugin into tree at original position, shifting original to right
    new_plugin = old_plugin.add_sibling(pos='left', instance=new_plugin)

    # This does not seem to stick for some reason
    #for child in children:
    #    child.move(target=new_plugin, pos='last-child')
    
    new_plugin = new_plugin.__class__.objects.get(pk=new_plugin.pk)
    old_plugin = old_plugin.__class__.objects.get(pk=old_plugin.pk)
    copy_plugins_to_placeholder(plugins=old_plugin.get_descendants(), placeholder=old_plugin.placeholder, root_plugin=new_plugin)
    
    new_plugin.copy_relations(old_plugin)
    new_plugin.post_copy(old_plugin, [(new_plugin, old_plugin),])
    
    # in case this is a child of a TextPlugin that needs
    # its content updated with the newly copied plugin
    if new_plugin.parent:
        parent.post_copy(parent, [(new_plugin, old_plugin),])
        
    old_plugin.delete()

    return new_plugin

def convert_aldryn_to_djangocms_style():
    for style in Style.objects.all():
        new_plugin = migrateStyle(style)
    dstyles = CMSPlugin.objects.filter(plugin_type='DjangoCMSStylePlugin')
    for ds in dstyles:
        ds.plugin_type = 'StylePlugin'
        ds.save()

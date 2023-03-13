from django import forms
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe


class ContentTypeSelect(forms.Select):
    def __init__(self, lookup_id='lookup_id_object_id', raw_fk='id_object_id', attrs=None, choices=()):
        self.lookup_id = lookup_id
        self.raw_fk = raw_fk
        super().__init__(attrs, choices)
    
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer=None)

        choices = self.choices
        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)
        for choice in choices:
            if hasattr(choice[0],'value'):
                ctype = ContentType.objects.get(pk=choice[0].value)
                rev = reverse("admin:%s_%s_changelist" % (ctype.app_label, ctype.model))+f'?_to_field={ctype.model_class()._meta.pk.name}'
                choiceoutput += f'"{ str(choice[0])}":"{rev}",'
        choiceoutput += '};'
        script = """<script type="text/javascript">
           
            %(choiceoutput)s
               const selectElement = document.querySelector('#%(id)s');
                selectElement.onchange = function(event){
                    document.querySelector('#%(fk_id)s').setAttribute('href',%(id)s_choice_urls[event.target.value]);
                    document.querySelector('#%(raw_fk)s').value='';
                }           
            </script>""" % {
                'choiceoutput': choiceoutput,
                'id': 'id_content_type',
                'fk_id': self.lookup_id,
                'raw_fk': self.raw_fk
            }

        output += script
        return mark_safe(u''.join(output))
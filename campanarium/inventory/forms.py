from django import forms

from .models import Bell, Bell_Founder, Bell_Tower, Carillon_Bell, Feedback


class BootstrapModelForm(forms.ModelForm):
    """Applies the right Bootstrap class to each widget (select / checkbox / date
    / text) and renders date fields as native date pickers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            else:
                widget.attrs.setdefault('class', 'form-control')
            if isinstance(widget, forms.DateInput):
                widget.input_type = 'date'


class BellForm(forms.ModelForm):
    """Create/edit a bell. Only the bell's own attributes live here; links to a
    founder, tower or carillon are separate relationships (see the guidance panel
    on the add page) and are managed on their own once the bell exists."""

    class Meta:
        model = Bell
        fields = [
            'name', 'function', 'year', 'pitch',
            'weight', 'height', 'diameter',
            'inscription', 'ornaments', 'profile',
            'installation', 'comments',
        ]
        widgets = {
            'inscription': forms.TextInput(attrs={'placeholder': 'Bijv. "MARIA VOCOR 1503"'}),
            'ornaments': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Reliëfs, wapenschilden, randversieringen, ...'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Geschiedenis, bronnen, bijzonderheden, ...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Bijv. "Roland" of "Klok 3"'}),
            'pitch': forms.TextInput(attrs={'placeholder': 'Bijv. "cis1"'}),
            'profile': forms.TextInput(attrs={'placeholder': 'Bijv. "zwaar", "licht", "medium"'}),
            'installation': forms.TextInput(attrs={'placeholder': 'Bijv. "vast opgehangen", "luidklok aan juk"'}),
        }
        # Extra guidance shown under each field, on top of the model's own help_text.
        help_texts = {
            'name': 'De eigennaam van de klok, of een werknaam als er geen officiële naam is.',
            'function': 'Kies waarvoor de klok dient. Bepaalt mee hoe ze in de inventaris gefilterd wordt.',
            'year': 'Het gietjaar (tussen 600 en 2100). Laat leeg indien onbekend.',
            'pitch': 'De slagtoon volgens de gangbare notatie (bijv. cis1). Boventonen voeg je later per klok toe.',
            'weight': 'Gewicht in kilogram.',
            'height': 'Hoogte van de klokmantel in centimeter.',
            'diameter': 'Onderdiameter in centimeter — de belangrijkste maat voor de toon.',
            'inscription': 'Neem de inscriptie letterlijk over, inclusief spelling en jaartallen.',
            'ornaments': 'Beschrijving van versieringen: friezen, medaillons, wapens, ...',
            'profile': 'Het klokprofiel (de wanddikte-verhouding). Vrij tekstveld.',
            'installation': 'Hoe de klok is opgehangen of opgesteld.',
            'comments': 'Alle overige informatie en verwijzingen naar bronnen.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap styling uniformly.
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')
        # A friendly blank choice makes "no function chosen yet" explicit.
        self.fields['function'].choices = [('', '— Kies een functie —')] + list(Bell.FUNCTION_CHOICES)


class FeedbackForm(forms.ModelForm):
    """Simple feedback form for beta testers. page_url and created_by are filled
    in by the view, not by the tester."""

    class Meta:
        model = Feedback
        fields = ['subject', 'message', 'contact']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Waar gaat het over?'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Wat werkt goed, wat niet, of wat mis je?'}),
            'contact': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Naam of e-mail (optioneel)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = False
        self.fields['message'].required = True  # the one thing we actually need


# --- Linking a bell to a gieter / toren / beiaard from the frontend ----------
# Each form edits one junction row; the `bell` side is set by the view from the
# URL, so it is not a form field.

class BellFounderForm(BootstrapModelForm):
    class Meta:
        model = Bell_Founder
        fields = ['founder', 'type_of_work', 'date_of_work', 'is_primary_founder']


class BellTowerForm(BootstrapModelForm):
    class Meta:
        model = Bell_Tower
        fields = ['tower', 'start_date', 'end_date', 'is_current_location', 'installation_details']
        widgets = {'installation_details': forms.Textarea(attrs={'rows': 2})}


class CarillonBellForm(BootstrapModelForm):
    class Meta:
        model = Carillon_Bell
        fields = ['carillon', 'relative_pitch', 'start_date', 'end_date']

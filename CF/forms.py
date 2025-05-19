from django import forms
from .models import (
    Region, Prefecture, SousPrefecture, Commune,
    Secteur, CentreFormation, DocumentAdministratif,
    PublicCible, PersonneReference
)

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['nom']


class PrefectureForm(forms.ModelForm):
    class Meta:
        model = Prefecture
        fields = ['nom', 'region']


class SousPrefectureForm(forms.ModelForm):
    class Meta:
        model = SousPrefecture
        fields = ['nom', 'prefecture']


class CommuneForm(forms.ModelForm):
    class Meta:
        model = Commune
        fields = ['nom', 'sous_prefecture']


class SecteurForm(forms.ModelForm):
    class Meta:
        model = Secteur
        fields = ['nom']


class PublicCibleForm(forms.ModelForm):
    class Meta:
        model = PublicCible
        fields = ['nom']


class CentreFormationForm(forms.ModelForm):
    class Meta:
        model = CentreFormation
        fields = [
            'secteurs', 'commune', 'intitule', 'sigle',
            'public_cibles', 'adresse', 'telephone', 'email', 'capacite_max'
        ]
        widgets = {
            'secteurs': forms.CheckboxSelectMultiple(attrs={}),
            'public_cibles': forms.CheckboxSelectMultiple(attrs={}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['secteurs', 'public_cibles']:
                field.widget.attrs['class'] = 'form-control'


class DocumentAdministratifForm(forms.ModelForm):
    class Meta:
        model = DocumentAdministratif
        fields = [
            'contrat_bail', 'titre_foncier', 'autre_document',
            'immatriculation_cnss', 'immatriculation_acfpe',
            'acquittement_fiscal', 'agrement_valide'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PersonneReferenceForm(forms.ModelForm):
    class Meta:
        model = PersonneReference
        fields = ['nom', 'prenom', 'telephone', 'email', 'fonction_libre']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


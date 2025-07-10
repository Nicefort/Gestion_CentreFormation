from django import forms
from .models import * 

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ["numero", "nom"]
        widgets = {
            "numero": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Numéro de la région"}
            ),
            "nom": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nom de la région"}
            ),
        }


class PrefectureForm(forms.ModelForm):
    class Meta:
        model = Prefecture
        fields = ["nom", "region"]


class SousPrefectureForm(forms.ModelForm):
    class Meta:
        model = SousPrefecture
        fields = ["nom", "prefecture"]


class CommuneForm(forms.ModelForm):
    class Meta:
        model = Commune
        fields = ["nom", "sous_prefecture"]


class SecteurForm(forms.ModelForm):
    class Meta:
        model = Secteur
        fields = ["nom"]


class PublicCibleForm(forms.ModelForm):
    class Meta:
        model = PublicCible
        fields = ["nom"]


class CentreFormationForm(forms.ModelForm):
    class Meta:
        model = CentreFormation
        fields = [
            "intitule",
            "sigle",
            "categorie",  # ✅ Champ ajouté
            "commune",
            "adresse",
            "telephone",
            "email",
        ]
        widgets = {
            "categorie": forms.Select(attrs={"class": "form-control"}),
            "intitule": forms.TextInput(attrs={"class": "form-control"}),
            "sigle": forms.TextInput(attrs={"class": "form-control"}),
            "commune": forms.Select(attrs={"class": "form-control"}),
            "adresse": forms.TextInput(attrs={"class": "form-control"}),
            "telephone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class DocumentAdministratifForm(forms.ModelForm):
    class Meta:
        model = DocumentAdministratif
        fields = [
            "contrat_bail",
            "titre_foncier",
            "autre_document",
            "immatriculation_cnss",
            "immatriculation_acfpe",
            "acquittement_fiscal",
            "agrement_valide",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class PersonneReferenceForm(forms.ModelForm):
    class Meta:
        model = PersonneReference
        fields = ["nom", "prenom", "telephone", "email", "fonction_libre"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

class DomaineActiviteCapaciteForm(forms.ModelForm):
    class Meta:
        model = DomaineActiviteCapacite
        fields = [
            "annee_experience",
            "secteurs",
            "public_cibles",
            "liste_activites",
            "activites_populaires",
            "capacite_max",
            "nombre_salles",
            "ListeAtelier",
        ]
        widgets = {
            "secteurs": forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            "public_cibles": forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            "liste_activites": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "activites_populaires": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "ListeAtelier": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "annee_experience": forms.NumberInput(attrs={'class': 'form-control'}),
            "capacite_max": forms.NumberInput(attrs={'class': 'form-control'}),
            "nombre_salles": forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter classes CSS de bootstrap
        for field in self.fields:
            if field not in ["secteurs", "public_cibles"]:
                self.fields[field].widget.attrs["class"] = "form-control"
                
                
EXPERIENCE_CHOICES = [
    '1-2 ans',
    '2-5 ans',
    '5-10 ans',
    'plus de 10 ans',
]

NIVEAU_CHOICES = [
    'CAP',
    'CAPT',
    'BTS',
    'Licence Professionnelle',
    'Master Professionnel',
    'Doctorat',
]

class FormateurForm(forms.ModelForm):
    niveaux_formateur = forms.MultipleChoiceField(
        choices=Formateur.NIVEAU_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Niveaux du formateur",
        required=True
    )

    experience_formateur = forms.MultipleChoiceField(
        choices=Formateur.EXPERIENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Expérience du formateur",
        required=True  # Laisse True si tu veux que ce champ soit obligatoire
    )

    class Meta:
        model = Formateur
        fields = [
            'niveaux_formateur',
            'experience_formateur',
            'nombre_formateur_permanant',
            'nombre_formateur_nonpermanant'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['niveaux_formateur'].initial = self.instance.niveaux_formateur
            self.fields['experience_formateur'].initial = self.instance.experience_formateur

    def clean_experience_formateur(self):
        data = self.cleaned_data.get('experience_formateur')
        if not data:
            raise forms.ValidationError("Veuillez sélectionner au moins une option.")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.niveaux_formateur = self.cleaned_data['niveaux_formateur']
        instance.experience_formateur = self.cleaned_data['experience_formateur']
        if commit:
            instance.save()
        return instance

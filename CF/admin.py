from django.contrib import admin
from .models import (
    CentreFormation,
    DocumentAdministratif,
    DomaineActiviteCapacite,
    Formateur,
    PersonneReference,
    Region,
    Prefecture,
    SousPrefecture,
    Commune,
    Secteur,
)

# Ajoute les modèles dans l'admin
admin.site.register(CentreFormation)
admin.site.register(DocumentAdministratif)
admin.site.register(DomaineActiviteCapacite)
admin.site.register(Formateur)
admin.site.register(PersonneReference)
admin.site.register(Region)
admin.site.register(Prefecture)
admin.site.register(SousPrefecture)
admin.site.register(Commune)
admin.site.register(Secteur)



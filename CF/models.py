from django.db import models
import os,re


# ---------- ZONE GÉOGRAPHIQUE ----------


class Region(models.Model):
    numero = models.PositiveIntegerField(unique=True, help_text="Numéro de la région")
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ["numero"]

    def __str__(self):
        return f"Région N°{self.numero} : {self.nom}"


class Prefecture(models.Model):
    nom = models.CharField(max_length=50)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="prefectures"
    )

    class Meta:
        unique_together = ("nom", "region")

    def __str__(self):
        return f"{self.nom} ({self.region})"


class SousPrefecture(models.Model):
    nom = models.CharField(max_length=50)
    prefecture = models.ForeignKey(
        Prefecture, on_delete=models.CASCADE, related_name="sousprefectures"
    )

    class Meta:
        unique_together = ("nom", "prefecture")

    def __str__(self):
        return f"{self.nom} ({self.prefecture})"


class Commune(models.Model):
    nom = models.CharField(max_length=50)
    sous_prefecture = models.ForeignKey(
        SousPrefecture, on_delete=models.CASCADE, related_name="communes"
    )

    class Meta:
        unique_together = ("nom", "sous_prefecture")

    def __str__(self):
        return f"{self.nom} ({self.sous_prefecture})"


# ---------- DOMAINES ET CIBLES ----------


class Secteur(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nom


class PublicCible(models.Model):
    nom = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nom


# ---------- CENTRE DE FORMATION ----------


class CentreFormation(models.Model):
    CATEGORIE_CHOICES = [
        ('1e', '1ère catégorie'),
        ('2e', '2ème catégorie'),
        ('3e', '3ème catégorie'),
    ]

    intitule = models.CharField(max_length=100, unique=True)
    sigle = models.CharField(max_length=20, blank=True)
    categorie = models.CharField(
        max_length=2,
        choices=CATEGORIE_CHOICES,
        blank=True,
        verbose_name="Catégorie"
    )
    commune = models.ForeignKey(
        Commune, on_delete=models.CASCADE, related_name="centres"
    )
    adresse = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    def __str__(self):
        return self.intitule


# ---------- DOCUMENTS ADMINISTRATIFS ----------

def document_upload_path(instance, filename):
    # Vérifie que le centre existe et a un intitule
    try:
        nom_centre = instance.centre.intitule
    except AttributeError:
        nom_centre = "temp"

    # Nettoyer le nom : supprime les caractères spéciaux, remplace les espaces
    safe_nom = re.sub(r"[^\w\s-]", "", nom_centre).strip().replace(" ", "_")
    return os.path.join("documents", f"centre_{safe_nom}", filename)


class DocumentAdministratif(models.Model):
    centre = models.OneToOneField(
        CentreFormation, on_delete=models.CASCADE, related_name="document_administratif"
    )

    contrat_bail = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    titre_foncier = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    autre_document = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    immatriculation_cnss = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    immatriculation_acfpe = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    acquittement_fiscal = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )
    agrement_valide = models.FileField(
        upload_to=document_upload_path, blank=True, null=True
    )

    def __str__(self):
        return f"Documents pour {self.centre}"


# ---------- PERSONNE DE RÉFÉRENCE ----------


class PersonneReference(models.Model):
    centre = models.OneToOneField(
        CentreFormation, on_delete=models.CASCADE, related_name="personne_reference"
    )
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    fonction_libre = models.CharField(
        max_length=50, help_text="Ex : directeur, tuteur, etc."
    )


    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.fonction_libre})"


class DomaineActiviteCapacite(models.Model):
    centre = models.OneToOneField(
        CentreFormation,
        on_delete=models.CASCADE,
        related_name="domaine_activité_capacité"
    )
    annee_experience = models.PositiveIntegerField(default=0)
    secteurs = models.ManyToManyField(Secteur, related_name="centres")
    public_cibles = models.ManyToManyField(
        PublicCible, related_name="centres", blank=True
    )
    liste_activites = models.TextField(
        blank=True,
        help_text="Liste des activités proposées (ex: couture, menuiserie, informatique...)",
    )
    activites_populaires = models.TextField(
        blank=True, help_text="Activités les plus pratiquées ou demandées"
    )
    capacite_max = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de personnes pouvant être accueillies par jour"
    )
    nombre_salles = models.PositiveIntegerField(
        default=0,
        help_text="Nombre total de salles disponibles"
    )
    ListeAtelier = models.TextField(
        blank=True, help_text="Listes des ateliers et lieu de formation"
    )

    def __str__(self):
        return f"État physique de {self.centre.intitule}"
    
    
class Formateur(models.Model):
    centre = models.OneToOneField(
        'CentreFormation',
        on_delete=models.CASCADE,
        related_name="formateur"
    )

    nombre_formateur_permanant = models.PositiveIntegerField(default=0)
    nombre_formateur_nonpermanant = models.PositiveIntegerField(default=0)

    # Liste des niveaux disponibles (stockés comme texte séparé par virgule)
    NIVEAU_CHOICES = [
        ('CAP', 'CAP'),
        ('CAPT', 'CAPT'),
        ('BTS', 'BTS'),
        ('LP', 'Licence Professionnelle'),
        ('MP', 'Master Professionnel'),
        ('DOC', 'Doctorat'),
    ]
    niveaux_formateur = models.JSONField(default=list, blank=True)

    # Années d'expérience
    EXPERIENCE_CHOICES = [
        ('1-2', '1 à 2 ans'),
        ('2-5', '2 à 5 ans'),
        ('5-10', '5 à 10 ans'),
        ('10+', 'Plus de 10 ans'),
    ]
    annees_experience_formateur = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Formateur du centre {self.centre}"
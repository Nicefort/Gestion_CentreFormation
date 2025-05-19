from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import *
from .models import *
import pandas as pd


def region_view(request, pk=None):
    obj = get_object_or_404(Region, pk=pk) if pk else None
    preview_data = None
    form = RegionForm(instance=obj)  # Formulaire vide par défaut

    if request.method == "POST":

        # -- 1. Prévisualisation --
        if "preview" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_excel(fichier, engine='openpyxl')
                preview_data = df.to_dict(orient="records")
            except Exception as e:
                messages.error(request, f"Erreur de lecture du fichier : {e}")

        # -- 2. Importation --
        elif "import" in request.POST and "fichier" in request.FILES:
            fichier = request.FILES["fichier"]
            try:
                df = pd.read_excel(fichier, engine='openpyxl')
                for _, row in df.iterrows():
                    Region.objects.get_or_create(nom=row["nom"])
                messages.success(request, "Importation réussie !")
                return redirect("region")
            except Exception as e:
                messages.error(request, f"Erreur d'importation : {e}")

        # -- 3. Enregistrement manuel du formulaire --
        elif "save" in request.POST:
            form = RegionForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect("region")

        # -- 4. Suppression --
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("region")

    # -- Chargement standard --
    regions = Region.objects.all()
    return render(
        request,
        "pages/region.html",
        {
            "form": form,
            "regions": regions,
            "obj": obj,
            "preview_data": preview_data,
        },
    )

# View qui gere les prefectures
def prefecture_view(request, pk=None):
    if pk:
        obj = get_object_or_404(Prefecture, pk=pk)
        form = PrefectureForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = PrefectureForm(request.POST or None)

    preview_data = None  # <-- Pour stocker la prévisualisation

    if request.method == "POST":
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("prefecture")
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("prefecture")
        elif "preview" in request.POST:
            fichier = request.FILES["fichier"]
            df = pd.read_excel(fichier)
            request.session["df_prefecture"] = df.to_dict()

            messages.info(
                request,
                "Prévisualisation chargée. Cliquez sur 'Importer' pour confirmer.",
            )

            return render(
                request,
                "pages/prefecture.html",
                {
                    "form": form,
                    "prefectures": Prefecture.objects.all(),
                    "df_preview": df.to_dict(orient="records"),
                    "obj": obj,
                },
            )
        elif "import" in request.POST:
            data = request.session.pop("df_prefecture", None)
            if data:
                for row in data.values():
                    Prefecture.objects.create(**row)
            return redirect("prefecture")

    return render(
        request,
        "pages/prefecture.html",
        {
            "form": form,
            "prefectures": Prefecture.objects.all(),
            "obj": obj,
        },
    )


# Vue qui gere les Sous Prefectures
def sousprefecture_view(request, pk=None):
    if pk:
        obj = get_object_or_404(SousPrefecture, pk=pk)
        form = SousPrefectureForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = SousPrefectureForm(request.POST or None)

    if request.method == "POST":
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("sous_prefecture")
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("sous_prefecture")
        elif "preview" in request.POST:
            fichier = request.FILES["fichier"]
            df = pd.read_excel(fichier)
            request.session["df_sousprefecture"] = df.to_dict()
            messages.info(request, "Prévisualisation chargée.")
            return render(
                request,
                "pages/sousprefecture.html",
                {
                    "form": form,
                    "sousprefectures": SousPrefecture.objects.all(),
                    "df_preview": df.to_dict(orient="records"),
                    "obj": obj,
                },
            )
        elif "import" in request.POST:
            data = request.session.pop("df_sousprefecture", None)
            if data:
                for row in data.values():
                    SousPrefecture.objects.create(**row)
            return redirect("sous_prefecture")

    return render(
        request,
        "pages/sousprefecture.html",
        {
            "form": form,
            "sousprefectures": SousPrefecture.objects.all(),
            "obj": obj,
        },
    )


# Vue qui gere les Communes
def commune_view(request, pk=None):
    if pk:
        obj = get_object_or_404(Commune, pk=pk)
        form = CommuneForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = CommuneForm(request.POST or None)

    if request.method == "POST":
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("commune")
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("commune")
        elif "preview" in request.POST:
            fichier = request.FILES["fichier"]
            df = pd.read_excel(fichier)
            request.session["df_commune"] = df.to_dict()
            messages.info(request, "Prévisualisation chargée.")
            return render(
                request,
                "pages/commune.html",
                {
                    "form": form,
                    "communes": Commune.objects.all(),
                    "df_preview": df.to_dict(orient="records"),
                    "obj": obj,
                },
            )
        elif "import" in request.POST:
            data = request.session.pop("df_commune", None)
            if data:
                for row in data.values():
                    Commune.objects.create(**row)
            return redirect("commune")

    return render(
        request,
        "pages/commune.html",
        {
            "form": form,
            "communes": Commune.objects.all(),
            "obj": obj,
        },
    )


# Vue qui gere les Secteurs
def secteur_view(request, pk=None):
    if pk:
        obj = get_object_or_404(Secteur, pk=pk)
        form = SecteurForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = SecteurForm(request.POST or None)

    if request.method == "POST":
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("secteur")
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("secteur")
        elif "preview" in request.POST:
            fichier = request.FILES["fichier"]
            df = pd.read_excel(fichier)
            request.session["df_secteur"] = df.to_dict()
            messages.info(request, "Prévisualisation chargée.")
            return render(
                request,
                "pages/secteur.html",
                {
                    "form": form,
                    "secteurs": Secteur.objects.all(),
                    "df_preview": df.to_dict(orient="records"),
                    "obj": obj,
                },
            )
        elif "import" in request.POST:
            data = request.session.pop("df_secteur", None)
            if data:
                for row in data.values():
                    Secteur.objects.create(**row)
            return redirect("secteur")

    return render(
        request,
        "pages/secteur.html",
        {
            "form": form,
            "secteurs": Secteur.objects.all(),
            "obj": obj,
        },
    )


# Vue qui gere les Public Cible
def publiccible_view(request, pk=None):
    if pk:
        obj = get_object_or_404(PublicCible, pk=pk)
        form = PublicCibleForm(request.POST or None, instance=obj)
    else:
        obj = None
        form = PublicCibleForm(request.POST or None)

    if request.method == "POST":
        if "save" in request.POST and form.is_valid():
            form.save()
            return redirect("publiccible")
        elif "delete" in request.POST and obj:
            obj.delete()
            return redirect("publiccible")
        elif "preview" in request.POST:
            fichier = request.FILES["fichier"]
            df = pd.read_excel(fichier)
            request.session["df_publiccible"] = df.to_dict()
            messages.info(request, "Prévisualisation chargée.")
            return render(
                request,
                "pages/publiccible.html",
                {
                    "form": form,
                    "publiccibles": PublicCible.objects.all(),
                    "df_preview": df.to_dict(orient="records"),
                    "obj": obj,
                },
            )
        elif "import" in request.POST:
            data = request.session.pop("df_publiccible", None)
            if data:
                for row in data.values():
                    PublicCible.objects.create(**row)
            return redirect("publiccible")

    return render(
        request,
        "pages/publiccible.html",
        {
            "form": form,
            "publiccibles": PublicCible.objects.all(),
            "obj": obj,
        },
    )


def centre_formation_view(request):
    # Récupérer les données des formulaires de chaque étape
    centres = CentreFormation.objects.all()
    document =DocumentAdministratif.objects.all()
    
    form_centre = CentreFormationForm(request.POST or None)
    form_docs = DocumentAdministratifForm(request.POST or None, request.FILES or None)
    form_ref = PersonneReferenceForm(request.POST or None)

    # Si la méthode est POST et que les trois formulaires sont valides
    if request.method == "POST":
        if form_centre.is_valid() and form_docs.is_valid() and form_ref.is_valid():
            # Sauvegarder le CentreFormation
            centre = form_centre.save()

            # Sauvegarder les documents avec la clé étrangère vers CentreFormation
            doc = form_docs.save(commit=False)
            doc.centre = centre  # Associer le document au centre
            doc.save()

            # Sauvegarder la personne de référence avec la clé étrangère vers CentreFormation
            ref = form_ref.save(commit=False)
            ref.centre = centre  # Associer la référence au centre
            ref.save()

            # Message de succès
            messages.success(
                request, "Les informations ont été enregistrées avec succès !"
            )
            return redirect(
                "centre_formation"
            )  # Rediriger vers une page de succès après soumission

    # Rendre la page avec les formulaires
    return render(
        request,
        "pages/cf.html",
        {
            "form_centre": form_centre,
            "form_docs": form_docs,
            "form_ref": form_ref,
            "centres": centres,
            "document": document,
        },
    )


def index(request):
    return render(request, "pages/index.html")


# def calendar(request):
#    return render(request,"pages/index.html")

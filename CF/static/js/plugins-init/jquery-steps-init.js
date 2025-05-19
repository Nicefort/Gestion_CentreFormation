(function($) {
    "use strict";

    var form = $("#step-form-horizontal");
    form.children('div').steps({
        headerTag: "h4",
        bodyTag: "section",
        transitionEffect: "slideLeft",
        autoFocus: true,
        onStepChanging: function (event, currentIndex, newIndex) {
            // Valide l'étape actuelle avant de continuer
            return form.valid();
        },
        onFinishing: function (event, currentIndex) {
            // Valide toutes les étapes avant de terminer
            return form.valid();
        },
        onFinished: function (event, currentIndex) {
            // Bloquer l'action par défaut (#finish)
            event.preventDefault();
            
            // Soumettre le formulaire manuellement
            form.submit();
        }
    });

    // Initialisation de la validation
    form.validate({
        errorClass: "text-danger",
        errorElement: "small",
        rules: {
            // Exemple : Règles de validation pour certains champs
            "secteurs": { required: true },
            "email": { required: true, email: true }
        },
        messages: {
            // Messages d'erreur personnalisés
            "secteurs": "Ce champ est obligatoire.",
            "email": {
                required: "Veuillez entrer un email.",
                email: "Veuillez entrer un email valide."
            }
        }
    });

})(jQuery);
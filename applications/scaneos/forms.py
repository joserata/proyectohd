from django import forms

from .models import ScanTarget


TOOLS = [

    ("zap", "OWASP ZAP"),

    ("wapiti", "Wapiti"),

    ("sqlmap", "SQLMap"),

    ("nmap", "Nmap"),

    ("sslyze", "SSLyze"),

    ("nuclei", "Nuclei"),

    ("nikto", "Nikto"),

]


class TargetForm(forms.ModelForm):

    class Meta:

        model = ScanTarget

        fields = [

            "name",

            "url",

            "description",

            "active",

        ]

        widgets = {

            "name": forms.TextInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "Nombre del sistema",

                }

            ),

            "url": forms.URLInput(

                attrs={

                    "class": "form-control",

                    "placeholder": "http://127.0.0.1:8001",

                }

            ),

            "description": forms.Textarea(

                attrs={

                    "class": "form-control",

                    "rows": 3,

                    "placeholder": "Descripción del objetivo",

                }

            ),

            "active": forms.CheckboxInput(

                attrs={

                    "class": "form-check-input",

                }

            ),

        }


class ScanForm(forms.Form):

    tool = forms.ChoiceField(

        choices=TOOLS,

        widget=forms.Select(

            attrs={

                "class": "form-select",

            }

        )

    )

    target_url = forms.URLField(

        label="URL Objetivo",

        widget=forms.URLInput(

            attrs={

                "class": "form-control",

                "placeholder": "http://127.0.0.1:8001",

            }

        )

    )

    authenticated = forms.BooleanField(

        required=False,

        initial=False,

        widget=forms.CheckboxInput(

            attrs={

                "class": "form-check-input",

            }

        ),

        label="Escaneo autenticado"

    )

    recursive = forms.BooleanField(

        required=False,

        initial=True,

        widget=forms.CheckboxInput(

            attrs={

                "class": "form-check-input",

            }

        ),

        label="Escaneo recursivo"

    )

    max_depth = forms.IntegerField(

        initial=3,

        min_value=1,

        max_value=10,

        widget=forms.NumberInput(

            attrs={

                "class": "form-control",

            }

        ),

        label="Profundidad"

    )

    timeout = forms.IntegerField(

        initial=300,

        min_value=60,

        max_value=3600,

        widget=forms.NumberInput(

            attrs={

                "class": "form-control",

            }

        ),

        label="Timeout (segundos)"

    )
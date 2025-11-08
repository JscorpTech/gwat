from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

PAGES = [
    {
        "seperator": False,
        "items": [
            {
                "title": _("Home page"),
                "icon": "home",
                "link": reverse_lazy("admin:index"),
            }
        ],
    },
    {
        "title": _("Auth"),
        "separator": True,  # Top border
        "items": [
            {
                "title": _("Users"),
                "icon": "group",
                "link": reverse_lazy("admin:accounts_user_changelist"),
            },
            {
                "title": _("Group"),
                "icon": "group",
                "link": reverse_lazy("admin:auth_group_changelist"),
            },
        ],
    },
    {
        "title": _("Dashboard"),
        "seperator": True,
        "items": [
            {
                "title": _("Chargers"),
                "icon": "group",
                "link": reverse_lazy("admin:api_chargermodel_changelist"),
            },
            {
                "title": _("Connectors"),
                "icon": "group",
                "link": reverse_lazy("admin:api_connectormodel_changelist"),
            },
            {
                "title": _("Transactions"),
                "icon": "group",
                "link": reverse_lazy("admin:api_transactionmodel_changelist"),
            },
        ],
    },
]

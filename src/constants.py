# Constants for the application

# Service Provider IDs
DATAPASS_SERVICE_PROVIDER_ID = 999
"""
Hard-coded constant for DataPass service provider ID.
DataPass is the only special service provider that can create groups for other service providers.
"""

# Email domains
PERSONAL_EMAIL_DOMAINS = frozenset(
    {
        "9business.fr",
        "9online.fr",
        "adeli.biz",
        "akeonet.com",
        "aliceadsl.fr",
        "alsatis.net",
        "aol.com",
        "aricia.fr",
        "bbox.fr",
        "bouyguestelecom.fr",
        "cegetel.net",
        "club-internet.fr",
        "club.fr",
        "evc.net",
        "free.fr",
        "gmail.com",
        "gmail.fr",
        "gmx.com",
        "gmx.fr",
        "gmx.net",
        "googlemail.com",
        "hotmail.com",
        "hotmail.fr",
        "icloud.com",
        "idyle-telecom.com",
        "laposte.net",
        "lgtel.fr",
        "live.com",
        "live.fr",
        "mail.com",
        "mailo.com",
        "mailoo.org",
        "mcom.fr",
        "me.com",
        "msn.com",
        "netcourrier.com",
        "neuf.fr",
        "nordnet.fr",
        "numericable.com",
        "numericable.fr",
        "online.fr",
        "orange-business.fr",
        "orange.fr",
        "outlook.com",
        "outlook.fr",
        "ovh.fr",
        "ovh.net",
        "ozone.net",
        "pagesperso-orange.fr",
        "proton.me",
        "protonmail.com",
        "rtvc.fr",
        "sfr.fr",
        "telwan.fr",
        "tubeo.eu",
        "tutanota.com",
        "tv-com.net",
        "vialis.net",
        "voila.fr",
        "wanadoo.fr",
        "west-telecom.com",
        "wibox.fr",
        "yahoo.com",
        "yahoo.fr",
        "yandex.com",
        "ymail.com",
        "zoho.com",
    }
)
"""
Personal mail providers no user of a group may use.

A public agent is expected to be reached at their professional address, so an
address at one of these providers is refused rather than added to a group.
Matching is an exact, case-insensitive comparison of the part after the `@`:
a sub-domain such as `mail.gmail.com` is not one of these providers.
"""

PERSONAL_EMAIL_REFUSED_CODE = "PERSONAL_EMAIL_REFUSED"
"""
`detail` of the 400 raised for an address at a personal mail provider.

It is an error code rather than a message: the consuming service knows which
addresses it sent, branches on this code and writes its own wording for its
users. It must therefore not change.
"""

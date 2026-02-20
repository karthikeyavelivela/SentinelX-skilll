"""Vendor name normalization aliases for fuzzy matching."""

VENDOR_ALIASES = {
    # Microsoft
    "microsoft": ["ms", "microsoft corporation", "microsoft corp", "microsoft corp."],
    "apache": ["apache software foundation", "the apache software foundation", "asf"],
    "google": ["google llc", "google inc", "google inc.", "alphabet"],
    "oracle": ["oracle corporation", "oracle corp"],
    "redhat": ["red hat", "red hat inc", "red hat, inc.", "rh"],
    "canonical": ["canonical ltd", "canonical ltd."],
    "debian": ["debian project", "debian gnu/linux"],
    "linux": ["linux kernel organization", "linux foundation", "kernel.org"],
    "apple": ["apple inc", "apple inc.", "apple computer"],
    "cisco": ["cisco systems", "cisco systems inc", "cisco systems, inc."],
    "ibm": ["ibm corporation", "international business machines"],
    "vmware": ["vmware inc", "vmware, inc.", "broadcom vmware"],
    "sap": ["sap se", "sap ag"],
    "adobe": ["adobe systems", "adobe inc.", "adobe systems incorporated"],
    "fortinet": ["fortinet inc", "fortinet, inc."],
    "paloalto": ["palo alto networks", "palo alto", "pan-os"],
    "nginx": ["nginx inc", "f5 nginx"],
    "wordpress": ["wordpress.org", "automattic"],
    "php": ["php group", "the php group"],
    "python": ["python software foundation", "psf"],
    "nodejs": ["node.js foundation", "openjs foundation"],
    "jenkins": ["jenkins project", "cloudbees"],
    "elastic": ["elastic nv", "elasticsearch bv"],
    "mongodb": ["mongodb inc", "mongodb, inc."],
    "postgresql": ["postgresql global development group", "pgdg"],
    "mysql": ["mysql ab", "oracle mysql"],
    "openssl": ["openssl project", "openssl software foundation"],
    "curl": ["curl project", "daniel stenberg"],
    "jquery": ["jquery foundation", "openjs"],
}


def get_canonical_vendor(vendor: str) -> str:
    """Get canonical vendor name from any alias."""
    if not vendor:
        return ""
    vendor_lower = vendor.lower().strip()
    
    # Direct match
    if vendor_lower in VENDOR_ALIASES:
        return vendor_lower
    
    # Check aliases
    for canonical, aliases in VENDOR_ALIASES.items():
        if vendor_lower in [a.lower() for a in aliases]:
            return canonical
    
    return vendor_lower


PRODUCT_ALIASES = {
    "iis": ["internet information services", "internet_information_services"],
    "exchange": ["exchange server", "exchange_server"],
    "office": ["microsoft office", "ms office"],
    "windows_server": ["windows server", "win_server"],
    "edge": ["microsoft edge", "edge_chromium"],
    "chrome": ["google chrome", "chromium"],
    "firefox": ["mozilla firefox", "mozilla_firefox"],
    "safari": ["apple safari"],
    "tomcat": ["apache tomcat", "apache_tomcat"],
    "httpd": ["apache http server", "apache_http_server", "apache2"],
    "struts": ["apache struts", "apache_struts"],
    "log4j": ["apache log4j", "apache_log4j", "log4j2"],
}


def get_canonical_product(product: str) -> str:
    """Get canonical product name from any alias."""
    if not product:
        return ""
    product_lower = product.lower().strip().replace(" ", "_")
    
    for canonical, aliases in PRODUCT_ALIASES.items():
        if product_lower == canonical or product_lower in [a.lower().replace(" ", "_") for a in aliases]:
            return canonical
    
    return product_lower

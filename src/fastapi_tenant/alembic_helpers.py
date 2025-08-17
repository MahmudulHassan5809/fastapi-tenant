TENANT_TOKEN = "tenant"


def get_current_tenant_from_args(get_x):
    xargs = get_x(as_dictionary=True)
    return xargs.get(TENANT_TOKEN) or None

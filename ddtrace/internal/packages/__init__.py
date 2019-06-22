from ...vendor.packaging import markers, requirements, version

# Try to import `importlib.metadata` first, because everything is better than `pkg_resources`
# DEV: `importlib.metadata` is Python >= 3.8 only
try:
    from importlib.metadata import distributions

    def _get_all_packages():
        return dict(
            (d.metadata['name'], version.parse(d.version))
            for d in distributions()
            if 'name' in d.metadata
        )

except ImportError:
    # TODO: Should we just try to backport `importlib.metadata`?
    from ...vendor import pkg_resources

    def _get_all_packages():
        return dict(
            (d.project_name, version.parse(d.version))
            for d in pkg_resources.working_set
        )


_package_cache = _get_all_packages()


def get_package_list():
    global _package_cache
    return _package_cache


def get_package_version(name):
    global _package_cache
    return _package_cache.get(name)


def parse_requirement(req):
    if not isinstance(req, requirements.Requirement):
        req = requirements.Requirement(str(req))
    return req


def requirement_passes(req):
    req = parse_requirement(req)

    if req.marker and not req.marker.evaluate():
        return False

    v = get_package_version(req.name)
    if not v:
        return False

    return req.specifier.contains(v)


def parse_marker(m):
    if not isinstance(m, markers.Marker):
        m = markers.Marker(str(m))
    return m


def marker_passes(m):
    m = parse_marker(m)
    return m.evaluate()

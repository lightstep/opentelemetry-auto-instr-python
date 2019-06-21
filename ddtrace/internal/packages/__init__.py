from ...vendor.packaging import markers, requirements, version

# Try to import `importlib.metadata` first, because everything is better than `pkg_resources`
# DEV: `importlib.metadata` is Python >= 3.8 only
try:
    from importlib.metadata import distribution, distributions

    def _get_all_packages():
        return dict(
            (d.metadata['name'], version.parse(d.version))
            for d in distributions()
            if 'name' in d.metadata
        )

    def _get_package_version(name):
        try:
            dist = distribution(name)
            if dist:
                return dist.version
        except Exception:
            pass

        return None

except ImportError:
    # TODO: Should we just try to backport `importlib.metadata`?
    from ...vendor import pkg_resources

    def _get_all_packages():
        return dict(
            (d.project_name, version.parse(d.version))
            for d in pkg_resources.working_set
        )

    def _get_package_version(name):
        try:
            dist = pkg_resources.get_distribution(name)
            if dist:
                return dist.version
        except Exception:
            pass

        return None


_package_cache = None


def list_all_packages():
    global _package_cache
    if not _package_cache:
        _package_cache = _get_all_packages()

    return _package_cache


def get_package_version(name):
    global _package_cache
    if name in _package_cache:
        return _package_cache[name]

    v = _get_package_version(name)
    if v:
        v = version.parse(v)

    # Always cache, even if it was not found so we don't lookup again
    _package_cache[name] = v
    return v


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

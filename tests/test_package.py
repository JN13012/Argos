def test_packages_import() -> None:
    import argos
    import argos.backend.intel.osint as backend_osint
    import argos.osint
    from argos.backend.intel.osint.models import SearchScope
    from argos.osint.models import SearchScope as LegacySearchScope

    assert argos.__name__ == "argos"
    assert argos.osint.__name__ == "argos.osint"
    assert backend_osint.__name__ == "argos.backend.intel.osint"
    assert LegacySearchScope is SearchScope

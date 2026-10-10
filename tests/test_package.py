def test_packages_import() -> None:
    import argos
    import argos.osint

    assert argos.__name__ == "argos"
    assert argos.osint.__name__ == "argos.osint"

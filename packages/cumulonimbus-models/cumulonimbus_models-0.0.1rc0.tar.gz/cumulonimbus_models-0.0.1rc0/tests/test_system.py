

def test_system():
    from cumulonimbus_models.system import Software, SystemInfo, SystemUpdateRequest
    from cumulonimbus_models import installation_types

    assert SystemUpdateRequest(
        system_info=SystemInfo(
            os='test',
            hostname='test',
            software=[
                Software(
                    name='test',
                    version='test',
                    installation_method=installation_types.PIP,
                    installation_data={'test': 'test'},
                    config_data={'test': 'test'}
                )
            ]
        )
    )
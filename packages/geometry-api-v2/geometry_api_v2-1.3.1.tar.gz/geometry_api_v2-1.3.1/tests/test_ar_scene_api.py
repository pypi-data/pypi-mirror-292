from shapediver.geometry_api_v2.client import (
    ArSceneApi,
    Configuration,
    GltfApi,
    QueryGltfConversion,
    SessionApi,
)
from shapediver.geometry_api_v2.sd_client import SdClient


def test_metadata_and_downloads(utils, host):
    client = SdClient(Configuration(host))

    # Initialize a new session.
    ticket = utils.create_ticket()
    session_id = SessionApi(client).create_session_by_ticket(ticket).session_id

    with open("tests/data/Box.glb", "rb") as f:
        s = f.read()

        # Create AR scene from glTF file.
        res_upload = GltfApi(client).upload_gltf(
            session_id, s, QueryGltfConversion.SCENE
        )
        assert res_upload.gltf.scene_id is not None

        scene_id = res_upload.gltf.scene_id

    # Get metadata of an existing AR scene.
    res_metadata = ArSceneApi(client).get_ar_scene_metadata_with_http_info(scene_id)
    assert res_metadata.status_code == 200

    # Download the created AR scene as glTF.
    res_gltf = ArSceneApi(client).download_ar_scene_gltf(scene_id)
    assert len(res_gltf) > 0

    # Download the created AR scene as USDZ.
    res_usdz = ArSceneApi(client).download_ar_scene_usdz(scene_id)
    assert len(res_usdz) > 0

    # Close the session.
    SessionApi(client).close_session(session_id)

from typing import Any, Optional, Dict, NamedTuple

from archive_box.processing.video.config import TranscodeConfig

class CollectionConfig(NamedTuple):
    display_name: str
    storage: str
    sync: str

    # storage settings
    local_storage: Dict[str, Any] = {}

    # sync settings
    sync_b2_bucket_name: Optional[str] = None

    # transcoding
    transcode: Optional[TranscodeConfig] = None

from typing import Any, Optional, Dict, NamedTuple

from archive_box.processing.video.config import TranscodeConfig

class CollectionConfig(NamedTuple):
    display_name: str
    storage: str
    local_storage: Dict[str, Any] = {}
    transcode: Optional[TranscodeConfig] = None

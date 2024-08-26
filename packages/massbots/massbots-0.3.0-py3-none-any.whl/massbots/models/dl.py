from massbots.openapi import models


class _Video(models.DlVideo):
    @property
    def formats_cached(self):
        return {k: v for k, v in self.formats.items() if v.cached}

    @property
    def formats_uncached(self):
        return {k: v for k, v in self.formats.items() if not v.cached}


Video = _Video
VideoFormat = models.DlVideoFormat
FileId = models.DlFileID
Result = models.DlResult

from pipeline.compressors import CompressorBase


class CSSMinCompressor(CompressorBase):
    """
    CSS compressor based on the Python library cssmin
    (http://pypi.python.org/pypi/cssmin/).
    """

    def compress_css(self, js):
        from cssmin import cssmin
        return cssmin(js)

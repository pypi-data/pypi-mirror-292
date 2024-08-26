import enum

VBAN_SR_MASK      = 0x1F
class VBANSampleRates(enum.Enum):
    RATE_6000   = 0
    RATE_8000   = 7
    RATE_11025  = 14
    RATE_12000  = 1
    RATE_16000  = 8
    RATE_22050  = 15
    RATE_24000  = 2
    RATE_32000  = 9
    RATE_44100  = 16
    RATE_48000  = 3
    RATE_64000  = 10
    RATE_88200  = 17
    RATE_96000  = 4
    RATE_128000 = 11
    RATE_176400 = 18
    RATE_192000 = 5
    RATE_256000 = 12
    RATE_352800 = 19
    RATE_384000 = 6
    RATE_512000 = 13
    RATE_705600 = 20
VBANSampleRatesEnum2SR = {
    VBANSampleRates.RATE_6000: 6000,
    VBANSampleRates.RATE_8000: 8000,
    VBANSampleRates.RATE_11025: 11025,
    VBANSampleRates.RATE_12000: 12000,
    VBANSampleRates.RATE_16000: 16000,
    VBANSampleRates.RATE_22050: 22050,
    VBANSampleRates.RATE_24000: 24000,
    VBANSampleRates.RATE_32000: 32000,
    VBANSampleRates.RATE_44100: 44100,
    VBANSampleRates.RATE_48000: 48000,
    VBANSampleRates.RATE_64000: 64000,
    VBANSampleRates.RATE_88200: 88200,
    VBANSampleRates.RATE_96000: 96000,
    VBANSampleRates.RATE_128000: 128000,
    VBANSampleRates.RATE_176400: 176400,
    VBANSampleRates.RATE_192000: 192000,
    VBANSampleRates.RATE_256000: 256000,
    VBANSampleRates.RATE_352800: 352800,
    VBANSampleRates.RATE_384000: 384000,
    VBANSampleRates.RATE_512000: 512000,
    VBANSampleRates.RATE_705600: 705600
}
VBANSampleRatesSR2Enum = {v: k for k, v in VBANSampleRatesEnum2SR.items()}

VBAN_BIT_RESOLUTION_MASK = 0x07
class VBANBitResolution(enum.Enum):
    VBAN_BITFMT_8_INT        = 0
    VBAN_BITFMT_16_INT       = 1
    VBAN_BITFMT_24_INT       = 2
    VBAN_BITFMT_32_INT       = 3
    VBAN_BITFMT_32_FLOAT     = 4
    VBAN_BITFMT_64_FLOAT     = 5
    VBAN_BITFMT_12_INT       = 6
    VBAN_BITFMT_10_INT       = 7
    VBAN_BIT_RESOLUTION_MAX  = 8

VBAN_CODEC_MASK = 0xF0
class VBANCodec(enum.Enum):
    VBAN_CODEC_PCM              = 0x00
    VBAN_CODEC_VBCA             = 0x10
    VBAN_CODEC_VBCV             = 0x20
    VBAN_CODEC_UNDEFINED_3      = 0x30
    VBAN_CODEC_UNDEFINED_4      = 0x40
    VBAN_CODEC_UNDEFINED_5      = 0x50
    VBAN_CODEC_UNDEFINED_6      = 0x60
    VBAN_CODEC_UNDEFINED_7      = 0x70
    VBAN_CODEC_UNDEFINED_8      = 0x80
    VBAN_CODEC_UNDEFINED_9      = 0x90
    VBAN_CODEC_UNDEFINED_10     = 0xA0
    VBAN_CODEC_UNDEFINED_11     = 0xB0
    VBAN_CODEC_UNDEFINED_12     = 0xC0
    VBAN_CODEC_UNDEFINED_13     = 0xD0
    VBAN_CODEC_UNDEFINED_14     = 0xE0
    VBAN_CODEC_USER             = 0xF0


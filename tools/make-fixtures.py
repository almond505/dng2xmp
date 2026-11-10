#!/usr/bin/env python3
"""Generate synthetic DNG/TIFF fixtures for testing the converter.

Usage: python3 tools/make-fixtures.py <out_dir>
The files are minimal classic-TIFF containers (no real image data) with an
XMP packet in tag 700, plus variants for the fallback and error paths.
"""
import os, struct, sys, zipfile

OUT = sys.argv[1] if len(sys.argv) > 1 else "fixtures"
os.makedirs(OUT, exist_ok=True)

def xmp(desc_attrs, children="", prefix="crs", about=""):
    return f'''<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 79.217bca6, 2021/06/14-18:28:11">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="{about}"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:{prefix}="http://ns.adobe.com/camera-raw-settings/1.0/"
    xmp:CreatorTool="Adobe Lightroom"
    {desc_attrs.replace("crs:", prefix + ":")}>
{children.replace("crs:", prefix + ":")}
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
{" " * 200}
<?xpacket end="w"?>'''.encode("utf-8")

CURVE = '''   <crs:ToneCurvePV2012>
    <rdf:Seq>
     <rdf:li>0, 18</rdf:li>
     <rdf:li>64, 58</rdf:li>
     <rdf:li>128, 132</rdf:li>
     <rdf:li>192, 204</rdf:li>
     <rdf:li>255, 245</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Red><rdf:Seq><rdf:li>0, 0</rdf:li><rdf:li>128, 138</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012Red>
   <crs:ToneCurvePV2012Green><rdf:Seq><rdf:li>0, 0</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012Green>
   <crs:ToneCurvePV2012Blue><rdf:Seq><rdf:li>0, 12</rdf:li><rdf:li>128, 120</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012Blue>
'''
LOOK = '''   <crs:Look>
    <rdf:Description crs:Name="Adobe Color" crs:Amount="0.85" crs:UUID="B952C231111CD8E0ECCF14B86BAA7077" crs:SupportsAmount="false" crs:SupportsMonochrome="false" crs:SupportsOutputReferred="false" crs:Copyright="© 2018 Adobe Systems, Inc.">
     <crs:Group><rdf:Alt><rdf:li xml:lang="x-default">Profiles</rdf:li></rdf:Alt></crs:Group>
     <crs:Parameters>
      <rdf:Description crs:Version="15.0" crs:ProcessVersion="11.0" crs:ConvertToGrayscale="False" crs:CameraProfile="Adobe Standard" crs:LookTable="E1095149FDB39D7A057BAB208837E2E1" crs:Contrast2012="-99">
       <crs:ToneCurvePV2012><rdf:Seq><rdf:li>0, 0</rdf:li><rdf:li>22, 16</rdf:li><rdf:li>255, 255</rdf:li></rdf:Seq></crs:ToneCurvePV2012>
      </rdf:Description>
     </crs:Parameters>
    </rdf:Description>
   </crs:Look>
'''
LOOK_RGB_MISSING = LOOK.replace('crs:LookTable="E1095149FDB39D7A057BAB208837E2E1"', 'crs:RGBTable="AABBCCDDEEFF00112233445566778899"').replace("Adobe Color", "Film Warm & <Faded>".replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
POINT = '''   <crs:PointColors><rdf:Seq><rdf:li>3.01, 0.42, 0.63, 12.0, -4.0, 0.0, 0.25, 0.55, 0.75, 1.0, 0.3, 0.5, 0.7, 1.0, 0.0, 0.1, 0.9, 1.0, 1</rdf:li></rdf:Seq></crs:PointColors>
'''
MASK = '''   <crs:MaskGroupBasedCorrections><rdf:Seq><rdf:li><rdf:Description crs:What="Correction" crs:LocalExposure2012="0.5"/></rdf:li></rdf:Seq></crs:MaskGroupBasedCorrections>
'''

FULL_ATTRS = '''crs:Version="16.0" crs:ProcessVersion="15.4" crs:WhiteBalance="As Shot" crs:Temperature="5600" crs:Tint="+8"
    crs:Exposure2012="+0.35" crs:Contrast2012="+24" crs:Highlights2012="-62" crs:Shadows2012="+41" crs:Whites2012="+12" crs:Blacks2012="-18"
    crs:Texture="+6" crs:Clarity2012="+10" crs:Dehaze="+4" crs:Vibrance="+14" crs:Saturation="-8" crs:ConvertToGrayscale="False"
    crs:ToneCurveName2012="Custom" crs:ParametricShadows="0" crs:ParametricDarks="-6" crs:ParametricLights="+5" crs:ParametricHighlights="0"
    crs:ParametricShadowSplit="25" crs:ParametricMidtoneSplit="50" crs:ParametricHighlightSplit="75"
    crs:HueAdjustmentRed="+4" crs:HueAdjustmentOrange="-6" crs:SaturationAdjustmentBlue="-22" crs:LuminanceAdjustmentGreen="-10" crs:SaturationAdjustmentAqua="-15"
    crs:ColorGradeMidtoneHue="32" crs:ColorGradeMidtoneSat="8" crs:ColorGradeShadowLum="-4" crs:ColorGradeHighlightLum="+3" crs:ColorGradeGlobalHue="0" crs:ColorGradeBlending="60"
    crs:SplitToningShadowHue="210" crs:SplitToningShadowSaturation="12" crs:SplitToningHighlightHue="40" crs:SplitToningHighlightSaturation="16" crs:SplitToningBalance="+10"
    crs:ShadowTint="+3" crs:RedHue="+8" crs:RedSaturation="+5" crs:GreenHue="-4" crs:GreenSaturation="0" crs:BlueHue="-12" crs:BlueSaturation="+18"
    crs:GrainAmount="18" crs:GrainSize="25" crs:GrainFrequency="50" crs:GrainSeed="1234567"
    crs:PostCropVignetteAmount="-14" crs:PostCropVignetteMidpoint="50" crs:PostCropVignetteFeather="50" crs:PostCropVignetteRoundness="0" crs:PostCropVignetteStyle="1" crs:PostCropVignetteHighlightContrast="0"
    crs:Sharpness="40" crs:SharpenRadius="+1.0" crs:SharpenDetail="25" crs:SharpenEdgeMasking="0" crs:LuminanceSmoothing="0" crs:ColorNoiseReduction="25" crs:ColorNoiseReductionDetail="50"
    crs:LensProfileEnable="1" crs:LensProfileSetup="LensDefaults" crs:AutoLateralCA="1" crs:DefringePurpleAmount="0" crs:PerspectiveVertical="0" crs:LensManualDistortionAmount="0" crs:VignetteAmount="0"
    crs:CropTop="0.02" crs:CropLeft="0" crs:CropBottom="1" crs:CropRight="0.98" crs:CropAngle="0" crs:HasCrop="True" crs:AlreadyApplied="False"
    crs:CameraProfile="Adobe Standard" crs:CameraProfileDigest="1DEADBEEF1DEADBEEF1DEADBEEF1DEAD" crs:RawFileName="IMG_0042.DNG"
    crs:HDREditMode="0" crs:OverrideLookVignette="False" crs:HasSettings="True"'''

def tiff(packet, le=True, tag=700, extra_tail=b"", pad_to=0, bigtiff=False, xmp_offset_override=None, packet_in_body=None):
    """Classic TIFF with IFD0: ImageWidth, ImageLength, XMP (tag 700), DNGVersion."""
    e = "<" if le else ">"
    bo = b"II" if le else b"MM"
    if bigtiff:
        head = bo + struct.pack(e + "HHHQ", 43, 8, 0, 0)
        body = head + (packet_in_body or b"")
        return body + extra_tail + b"\0" * max(0, pad_to - len(body) - len(extra_tail))
    entries = []
    ifd_off = 8
    n = 4
    ifd_size = 2 + n * 12 + 4
    data_off = ifd_off + ifd_size
    pkt = packet or b""
    entries.append((256, 4, 1, 16))
    entries.append((257, 4, 1, 16))
    if packet is not None:
        off = data_off if xmp_offset_override is None else xmp_offset_override
        entries.append((tag, 7, len(pkt), off))
    else:
        entries.append((305, 2, 4, struct.unpack(e + "I", b"Lr\0\0" if le else b"Lr\0\0")[0]))
    entries.append((50706, 1, 4, struct.unpack(e + "I", bytes([1, 4, 0, 0]))[0]))
    entries.sort()
    out = bo + struct.pack(e + "HI", 42, ifd_off)
    out += struct.pack(e + "H", n)
    for t, ty, c, v in entries:
        out += struct.pack(e + "HHII", t, ty, c, v)
    out += struct.pack(e + "I", 0)
    out += pkt
    if packet_in_body:
        out += b"\x00" * 1000 + packet_in_body
    out += extra_tail
    if pad_to and len(out) < pad_to:
        # pseudo image data: repeating pattern, not zeros, so the scanner reads real bytes
        chunk = bytes(range(256)) * 4096
        need = pad_to - len(out)
        out += (chunk * (need // len(chunk) + 1))[:need]
    return out

def w(name, data):
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(data)
    print(f"{name:34s} {len(data):>10d} bytes")

full = xmp(FULL_ATTRS, CURVE + LOOK + POINT + MASK)
w("01-full-LE.dng", tiff(full, le=True))
w("02-full-BE.dng", tiff(full, le=False))
w("03-big-60MB.dng", tiff(full, le=True, pad_to=60 * 1024 * 1024))
# Different prefix for the crs namespace, settings as child elements
alt = xmp('crs:Version="15.0" crs:ProcessVersion="11.0" crs:CameraProfile="Embedded"',
          '   <crs:Contrast2012>+30</crs:Contrast2012>\n   <crs:Vibrance>-5</crs:Vibrance>\n' + CURVE, prefix="cr")
w("04-other-prefix-embedded-profile.dng", tiff(alt))
# No tag 700 → byte-scan fallback; packet placed across a 4 MiB chunk boundary
body_pkt = xmp('crs:Version="16.0" crs:ProcessVersion="15.4" crs:Contrast2012="+15" crs:Saturation="-20"', LOOK_RGB_MISSING)
pre = 4 * 1024 * 1024 - 400
data = tiff(None, le=True)
data += bytes((i * 7) & 0xFF for i in range(pre - len(data))) + body_pkt + b"\x11" * 5000
w("05-fallback-scan-boundary.dng", data)
# Ambiguous: no tag 700, two different packets with develop settings
p1 = xmp('crs:Version="16.0" crs:ProcessVersion="15.4" crs:Contrast2012="+10"')
p2 = xmp('crs:Version="16.0" crs:ProcessVersion="15.4" crs:Contrast2012="-40" crs:Vibrance="+20"', LOOK)
w("06-ambiguous-two-packets.dng", tiff(None) + b"\x00" * 300 + p1 + b"\x55" * 900 + p2)
# No crs data
plain = b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:tiff="http://ns.adobe.com/tiff/1.0/" tiff:Make="Canon"/></rdf:RDF></x:xmpmeta>'
w("07-unedited.dng", tiff(plain))
# Damaged: NUL inside the XML
bad = bytearray(full); i = bad.index(b'crs:Contrast2012'); bad[i - 1] = 0
w("08-damaged-nul.dng", tiff(bytes(bad)))
# Damaged: tag 700 offset past end of file → reported, then byte scan finds nothing
w("09-bad-offset.dng", tiff(full[:50], xmp_offset_override=10_000_000))
# Truncated XML (no closing)
w("10-truncated.dng", tiff(full[: len(full) // 2]))
# Not TIFF
w("11-not-a-dng.dng", b"\xff\xd8\xff\xe0JFIF fake jpeg" + b"\0" * 100)
# BigTIFF variant with packet in body → unsupported container, scan fallback
w("12-bigtiff.dng", tiff(None, bigtiff=True, packet_in_body=b"\0" * 64 + full))
# Invalid UTF-8 in packet
badu = full.replace(b'crs:Contrast2012="+24"', b'crs:Contrast2012="+2\xff"')
w("13-bad-utf8.dng", tiff(badu))
# Preset name collision test (same base names in zip)
with zipfile.ZipFile(os.path.join(OUT, "20-batch.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("roll1/Sunset.dng", tiff(full))
    z.writestr("roll2/Sunset.dng", tiff(xmp('crs:Version="16.0" crs:ProcessVersion="15.4" crs:Contrast2012="+5"')))
    z.writestr("roll2/notes.txt", "hello")
    z.writestr("__MACOSX/roll1/._Sunset.dng", "junk")
    z.writestr("CON.dng", tiff(full, le=False))
print("zip: 20-batch.zip")
open(os.path.join(OUT, "21-corrupt.zip"), "wb").write(b"PK\x03\x04 this is not really a zip" + b"\0" * 64)
print("zip: 21-corrupt.zip")

# nrn-diff

## Usage

```pycon
>>> from nrndiff import nrn_diff
>>> from neuron import h
>>> s1 = h.Section()
>>> s2 = h.Section()
>>> nrn_diff(s1, s2)
[]
>>> s2.L = s1.L * 2
>>> nrn_diff(s1, s2)
[
    <nrndiff._differences.SectionLengthDifference object at 0x7f52eb4d3310>,
    <nrndiff._differences.SegmentAreaDifference object at 0x7f52eb47de80>,
    <nrndiff._differences.SegmentVolumeDifference object at 0x7f52eb47d7c0>,
    <nrndiff._differences.SegmentInputResistanceDifference object at 0x7f52eb47df40>
]
```
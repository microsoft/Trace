import re


def test(l):
    assert ('@bundle(' in l) or ('@bundle\\' in l) or \
            (re.search(r'@.*\.bundle\(.*', l) is not None) or \
            (re.search(r'@.*\.bundle\\.*', l) is not None)

l = '@bundle()\njklasjdflksd'
test(l)

l = '@bundle\ ajsdkfldsjf'
test(l)

l = '@.....bundle(jkalsdfj'
test(l)
l = '@.....bundle\\jklasjdlfk'
test(l)
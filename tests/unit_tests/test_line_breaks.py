from opto import trace

@trace.bundle(trainable=True)
def test_line_breaks():
    # Test the line breaks in the trace output
    print('Hello, world!')
    return



x = test_line_breaks.parameter
x._data = x.data.replace('\n', '\\n')
print(repr(x.data))
test_line_breaks()

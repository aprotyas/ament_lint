from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr


def get_xunit_content(report, testname, elapsed):
    test_count = sum([max(len(r), 1) for r in report.values()])
    error_count = sum([len(r) for r in report.values()])
    data = {
        'testname': testname,
        'test_count': test_count,
        'error_count': error_count,
        'time': '%.3f' % round(elapsed, 3),
    }
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<testsuite
  name="%(testname)s"
  tests="%(test_count)d"
  failures="%(error_count)d"
  time="%(time)s"
>
''' % data

    for filename in sorted(report.keys()):
        errors = report[filename]

        if errors:
            # report each cppcheck error as a failing testcase
            for error in errors:
                data = {
                    'quoted_location': quoteattr(
                        '%s:%d' % (filename, error['line'])),
                    'severity': error['severity'],
                    'id': error['id'],
                    'quoted_message': quoteattr(error['msg']),
                }
                xml += '''  <testcase
    name=%(quoted_location)s
    classname="%(severity)s: %(id)s"
  >
      <failure message=%(quoted_message)s/>
  </testcase>
''' % data

        else:
            # if there are no cpplint errors report a single successful test
            data = {'quoted_location': quoteattr(filename)}
            xml += '''  <testcase
    name=%(quoted_location)s
    status="No errors"/>
''' % data

    # output list of checked files
    data = {
        'escaped_files': escape(''.join(['\n* %s' % r
                                         for r in sorted(report.keys())])),
    }
    xml += '''  <system-out>Checked files:%(escaped_files)s</system-out>
''' % data

    xml += '</testsuite>'
    return xml

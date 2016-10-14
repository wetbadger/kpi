
from kpi.models import Asset
from pprint import pprint
from collections import OrderedDict
import json
import string
import inspect
from copy import deepcopy


def _asset_constructor(fn):
    def _new(): return Asset(asset_type='survey', content=fn())
    return _new


def score_asset_content():
    return {
        u'survey': [
            {u'kobo--score-choices': u'nb7ud55',
             u'label': [u'Rate Los Angeles'],
             u'required': True,
             u'type': u'begin_score'},
            {u'label': [u'Food'], u'type': u'score__row'},
            # {u'label': [u'Music'], u'type': u'score__row'},
            # {u'label': [u'Night life'], u'type': u'score__row'},
            # {u'label': [u'Housing'], u'type': u'score__row'},
            # {u'label': [u'Culture'], u'type': u'score__row'},
            {u'type': u'end_score'}],
        u'choices': [
            # {u'label': [u'Great'],
            #  u'list_name': u'nb7ud55'},
            {u'label': [u'OK'],
             u'list_name': u'nb7ud55'},
            # {u'label': [u'Bad'],
            #  u'list_name': u'nb7ud55'}
        ],
    }

score_asset = _asset_constructor(score_asset_content)


def color_picker_asset_content():
    return {
        'survey': [
            {'type': 'select_multiple', 'label': 'select colors',
             'select_from_list_name': 'colors'}
        ],
        'choices': [
            {'list_name': 'colors', 'label': 'Red'},
            {'list_name': 'colors', 'label': 'Yellow'},
            {'list_name': 'colors', 'label': 'Blue'},
        ],
        'settings': {
            'form_title': 'color picker',
            'id_string': 'colorpik',
        }
    }

color_picker_asset = _asset_constructor(color_picker_asset_content)


def nonstandard_asset():
    return Asset(asset_type='survey', content={
        'survey': [
            {'type': 'select_one abc', 'Label': 'select a letter'},
            # todo: handle certain "expand" features after aliases are replaced
            # {'type': 'select1 abc', 'Label': 'select a letter'},
            {},
            {'misc_value': 'gets removed by _strip_empty_rows'},
        ],
        'choices': [
            {'list name': 'abc', 'label': letter}
             for letter in string.ascii_lowercase
        ]
    })


def jprint(c):
    print(json.dumps(c, indent=2))


def _r1(content, sheet_name='survey'):
    return content[sheet_name][0]


def _is_lambda(v):
    LAMBDA_TYPE = type(lambda: 0)
    return isinstance(v, LAMBDA_TYPE) and v.__name__ == '<lambda>'


def for_each_row(content, *args):
    sheet_names = ['survey', 'choices']
    if isinstance(args[0], basestring):
        _pass_sheet_name = False
        sheet_names = [args[0]]
        fn = args[1]
    else:
        _pass_sheet_name = True
        fn = args[0]
    _lambda = _is_lambda(fn)
    for _sheet_name in sheet_names:
        for row in content[_sheet_name]:
            args = [row]
            if _pass_sheet_name:
                args.append(_sheet_name)
            if _lambda:
                if not fn(*args):
                    raise AssertionError('"{}" failed on row: {}'.format(
                                                inspect.getsource(fn).strip(),
                                                json.dumps(row, indent=2)
                                            )
                                         )
            else:
                fn(*args)


def test_standardization_of_nonstandard_asset():
    a1 = nonstandard_asset()
    # standardize returns True if it passed the content through to the
    # "standardize_content_in_place()" method.
    assert a1._standardize(a1.content)

    # all content has a settings dict
    assert 'settings' in a1.content
    assert isinstance(a1.content['settings'], dict)

    # "Label" is changed to "label"
    assert 'label' in _r1(a1.content)
    assert _r1(a1.content)['type'] == 'select_one'
    assert _r1(a1.content)['select_from_list_name'] == 'abc'
    # $kuid has not been assigned yet
    for_each_row(a1.content, lambda row, s: '$kuid' not in row)
    for_each_row(a1.content, lambda row, s: 'name' not in row)

    # "list name" is changed to "list_name"
    assert 'list_name' in _r1(a1.content, 'choices')

    a1._strip_empty_rows(a1.content)
    assert len(a1.content['survey']) == 1

    # kuids are set
    a1._assign_kuids(a1.content)
    for_each_row(a1.content, lambda row, s: '$kuid' in row)

    # $autoname and $autovalue are set in `_autoname(...)`
    for_each_row(a1.content, 'survey', lambda row: '$autoname' not in row)
    for_each_row(a1.content, 'choices', lambda row: '$autovalue' not in row)
    a1._autoname(a1.content)
    for_each_row(a1.content, 'survey', lambda row: '$autoname' in row)
    for_each_row(a1.content, 'choices', lambda row: '$autovalue' in row)
    # at this point, asset.save() is complete.


def test_remove_empty_expressions():
    a1 = Asset(asset_type='survey', content={})

    c1 = {'survey': [{'relevant': ''}]}
    a1._remove_empty_expressions(c1)
    assert _r1(c1) == {}

    c1 = {'survey': [{'bind': None}]}
    a1._remove_empty_expressions(c1)
    assert _r1(c1) == {}


def test_save_transformations():
    a1 = Asset(asset_type='survey', content={})

    content = color_picker_asset_content()
    a1._standardize(content)
    a1._strip_empty_rows(content)
    a1._assign_kuids(content)
    form_title = a1.pop_setting(content, 'form_title')
    a1._autoname(content)
    assert 'schema' in content
    assert content['translations'] == [None]
    assert form_title == 'color picker'
    assert content['settings'] == {'id_string': 'colorpik'}
    # save complete!


def _compile_score_content(content):
    a1 = score_asset()
    a1._standardize(content)
    a1._strip_empty_rows(content)
    a1._assign_kuids(content)
    form_title = a1.pop_setting(content, 'form_title', 'a backup title')
    a1._autoname(content)
    assert form_title == 'a backup title'
    # at this stage, the save is complete

    a1._expand_kobo_qs(content)
    a1._autoname(content)
    a1._assign_kuids(content)
    return content


def _score_item(_r):
    r = deepcopy(_r)
    return [
        r.pop('type'),
        r.pop('$autoname', False),
        u' '.join(sorted(r.keys())),
    ]


def test_score_to_xlsform_structure():
    a1 = score_asset()
    content = _compile_score_content(score_asset_content())
    a1._populate_fields_with_autofields(content)
    assert content['settings'] == {}
    a1._append(content, settings={
        'style': 'pages',
    })
    content = OrderedDict(content)
    a1._xlsform_structure(content, ordered=True)

    # ensure 'schema' sheet is removed
    assert content.keys() == [u'survey', u'choices', u'settings']

    _rows = content['survey']
    for row in _rows:
        assert row.keys() == [u'type', u'name', u'label', u'appearance', u'required']
    assert _rows[0] == {u'type': u'begin_group',
                        u'appearance': u'field-list',
                        u'label': None,
                        u'required': None,
                        u'name': u'Rate_Los_Angeles',
                        }
    assert _rows[1] == {u'type': u'select_one nb7ud55',
                        u'appearance': u'label',
                        u'required': None,
                        u'name': u'Rate_Los_Angeles_header',
                        u'label': u'Rate Los Angeles',
                        }
    assert _rows[2] == {u'type': u'select_one nb7ud55',
                        u'appearance': u'list-nolabel',
                        u'name': u'Food',
                        u'label': u'Food',
                        u'required': u'true',
                        }


def test_score_question_compiles():
    content = _compile_score_content(score_asset_content())
    _rows = content['survey']

    assert _rows[0]['name'] == 'Rate_Los_Angeles'
    assert _rows[1]['name'] == 'Rate_Los_Angeles_header'
    assert _rows[2]['$autoname'] == 'Food'

    assert ([_score_item(r) for r in _rows]) == [
        [u'begin_group', u'Rate_Los_Angeles',
            u'$kuid appearance name'],
        [u'select_one', u'Rate_Los_Angeles_header',
            u'$kuid appearance label name select_from_list_name'],
        [u'select_one', u'Food',
            u'$kuid appearance label required select_from_list_name'],
        [u'end_group', False,
            u'$kuid']
    ]


def test_named_score_question_compiles():
    content = _compile_score_content({
        u'survey': [
            {u'kobo--score-choices': u'nb7ud55',
             u'label': [u'Rate Los Angeles'],
             u'required': True,
             u'name': 'skore',
             u'type': u'begin_score'},

            {u'label': [u'Food'], u'type': u'score__row'},

            {u'type': u'end_score'}],
        u'choices': [
            {u'label': [u'OK'],
             u'list_name': u'nb7ud55'},
        ],
    })

    _rows = content['survey']
    assert _rows[0]['name'] == 'skore'
    assert _rows[1]['name'] == 'skore_header'
    assert _rows[2]['$autoname'] == 'Food'

    def _score_item(_r):
        r = deepcopy(_r)
        return [
            r.pop('type'),
            r.pop('$autoname', False),
            u' '.join(sorted(r.keys())),
        ]

    assert ([_score_item(r) for r in _rows]) == [
        [u'begin_group', u'skore',
            u'$kuid appearance name'],
        [u'select_one', u'skore_header',
            u'$kuid appearance label name select_from_list_name'],
        [u'select_one', u'Food',
            u'$kuid appearance label required select_from_list_name'],
        [u'end_group', False,
            u'$kuid']
    ]

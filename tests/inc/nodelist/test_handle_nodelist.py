from json import dumps, loads
from random import choice

from ffflash.inc.nodelist import handle_nodelist


def test_handle_nodelist_without_nodelist(tmpdir, fffake):
    ff = fffake(tmpdir.join('api_file.json'), dry=True)

    assert handle_nodelist(ff) is False

    assert tmpdir.remove() is None


def test_handle_nodelist_invalid_nodelist_locations(tmpdir, fffake):
    apifile = tmpdir.join('api_file.json')
    apifile.write_text(dumps({'a': 'b'}), 'utf-8')
    for nodelist in [
        tmpdir.join('nodes.json'),
        'http://localhost/404/not-found/does/not/exist.json',
    ]:

        ff = fffake(apifile, nodelist=nodelist, dry=True)
        assert handle_nodelist(ff) is False

    assert tmpdir.remove() is None


def test_handle_nodelist_empty_nodelist(tmpdir, fffake):
    apifile = tmpdir.join('api_file.json')
    apifile.write_text(dumps({'a': 'b'}), 'utf-8')
    nl = tmpdir.join('nodes.json')
    nl.write_text(dumps(''), 'utf-8')

    ff = fffake(apifile, nodelist=nl, dry=True)
    assert handle_nodelist(ff) is False

    nl.write_text(dumps({'a': 'b'}), 'utf-8')
    ff = fffake(apifile, nodelist=nl, dry=True)
    assert handle_nodelist(ff) is False

    nl.write_text(dumps({
        'version': 2, 'nodes': [], 'updated_at': 'never'
    }), 'utf-8')
    ff = fffake(apifile, nodelist=nl, dry=True)
    assert handle_nodelist(ff) is False

    assert tmpdir.remove() is None


def test_handle_nodelist_count_some_nodes(tmpdir, fffake):
    apifile = tmpdir.join('api_file.json')
    apifile.write_text(dumps({
        'state': {'nodes': 0, 'description': ''}
    }), 'utf-8')
    nl = tmpdir.join('nodes.json')

    def _n(c, o):
        return {'status': {'clients': c, 'online': o}}

    dt = [(choice(range(42)), choice([True, False])) for _ in range(23)]
    nl.write_text(dumps({
        'version': 2, 'nodes': [
            _n(c, o) for c, o in dt
        ], 'updated_at': 'never'
    }), 'utf-8')

    ff = fffake(apifile, nodelist=nl, dry=True)

    assert ff.api.c.get('state').get('nodes') == 0
    assert handle_nodelist(ff) is True
    assert ff.api.c.get('state').get('nodes') == sum([o for _, o in dt])

    assert tmpdir.remove() is None


def test_handle_nodelist_dry_launch_rankfile(tmpdir, fffake):
    apifile = tmpdir.join('api_file.json')
    apifile.write_text(dumps({'a': 'b'}), 'utf-8')
    nl = tmpdir.join('nodes.json')
    nl.write_text(dumps({
        'version': 0, 'nodes': [], 'updated_at': 'never'
    }), 'utf-8')
    rf = tmpdir.join('rankfile.json')

    assert tmpdir.listdir() == [apifile, nl]
    ff = fffake(apifile, nodelist=nl, rankfile=rf, dry=True)

    assert handle_nodelist(ff) is False

    assert tmpdir.listdir() == [apifile, nl]
    assert tmpdir.remove() is None


def test_handle_nodelist_launch_rankfile(tmpdir, fffake):
    apifile = tmpdir.join('api_file.json')
    apifile.write_text(dumps({'a': 'b'}), 'utf-8')
    nl = tmpdir.join('nodes.json')
    nl.write_text(dumps({
        'version': 0, 'nodes': [], 'updated_at': 'never'
    }), 'utf-8')
    rf = tmpdir.join('rankfile.json')

    assert tmpdir.listdir() == [apifile, nl]
    ff = fffake(apifile, nodelist=nl, rankfile=rf)

    assert handle_nodelist(ff) is True
    assert tmpdir.listdir() == [apifile, nl, rf]

    res = loads(rf.read_text('utf-8'))
    assert res
    assert res.get('nodes') == []
    assert res.get('updated_at', False) != 'never'

    assert tmpdir.remove() is None

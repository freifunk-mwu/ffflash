from ffflash.inc.rankfile import handle_rankfile
from ffflash.lib.files import check_file_location, load_file
from ffflash.lib.remote import fetch_www_struct
from ffflash.lib.text import replace_text


def _nodelist_fetch(ff):
    '''
    Determines if ``--nodelist`` was a file or a url, and tries to fetch it.
    Validates nodelist to be json and to have the *version*, *nodes* and
    *updated_at* keys.

    :param ff: running :class:`ffflash.main.FFFlash` instance
    :return: the unpickled nodelist or ``False``/``None`` on error
    '''
    if not ff.access_for('nodelist'):
        return False

    ff.log('fetching nodelist {}'.format(ff.args.nodelist))

    nodelist = (
        load_file(ff.args.nodelist, fallback=None, as_yaml=False)
        if check_file_location(ff.args.nodelist, must_exist=True) else
        fetch_www_struct(ff.args.nodelist, fallback=None, as_yaml=False)
    )
    if not nodelist or not isinstance(nodelist, dict):
        return ff.log(
            'could not fetch nodelist {}'.format(ff.args.nodelist),
            level=False
        )

    if not all([(a in nodelist) for a in ['version', 'nodes', 'timestamp']]):
        return ff.log(
            'this is no nodelist {}'.format(ff.args.nodelist),
            level=False
        )

    ff.log('successfully fetched nodelist from {}'.format(ff.args.nodelist))
    return nodelist


def _nodelist_count(ff, nodelist):
    '''
    Count online nodes and sum up their clients from a nodelist.

    :param ff: running :class:`ffflash.main.FFFlash` instance
    :param nodelist: nodelist from :meth:`_nodelist_fetch`, should contain a
        list of dictionaries at the key *nodes*
    :return: Tuple of counted nodes and clients
    '''
    nodes, clients = 0, 0
    for node in nodelist.get('nodes', []):
        if node.get('nodeinfo', {}).get('system', {}).get('domain_code') == ff.args.site:
            if node.get('flags', {}).get('online', False):
                nodes += 1
                clients += node.get('statistics', {}).get('clients', 0)

    if not all([nodes, clients]):
        ff.log('your nodelist seems to be empty', level=False)

    ff.log('found {} nodes, {} clients'.format(nodes, clients))
    return nodes, clients


def _nodelist_dump(ff, nodes, clients):
    '''
    Store the counted numbers in the api-file.

    Sets the key ``state`` . ``nodes`` with the node number.

    Leaves ``state`` . ``description`` untouched, if any already present.
    If empty, or the pattern ``\[[\d]+ Nodes, [\d]+ Clients\]`` is matched,
    the numbers in the pattern will be replaced.

    :param ff: running :class:`ffflash.main.FFFlash` instance
    :param nodes: Number of online nodes
    :param clients: Number of their clients
    :return: ``True`` if :attr:`api` was modified else ``False``
    '''
    if not ff.access_for('nodelist'):
        return False

    modified = []
    if ff.api.pull('state', 'nodes') is not None:
        ff.api.push(nodes, 'state', 'nodes')
        ff.log('stored {} in state.nodes'.format(nodes))
        modified.append(True)

    descr = ff.api.pull('state', 'description')
    if descr is not None:
        new = '[{} Nodes, {} Clients]'.format(nodes, clients)
        new_descr = (replace_text(
            r'(\[[\d]+ Nodes, [\d]+ Clients\])', new, descr
        ) if descr else new)
        ff.api.push(new_descr, 'state', 'description')
        ff.log('stored {} nodes and {} clients in state.description'.format(
            nodes, clients
        ))
        modified.append(True)

    return any(modified)


def handle_nodelist(ff):
    '''
    Entry function to receive a ``--nodelist`` and store determined results
    into both :attr:`api` and ``--rankfile`` (if specified).

    :param ff: running :class:`ffflash.main.FFFlash` instance
    :return: ``True`` if :attr:`api` was modified else ``False``
    '''
    if not ff.access_for('nodelist'):
        return False

    nodelist = _nodelist_fetch(ff)
    if not nodelist:
        return False

    modified = []

    nodes, clients = _nodelist_count(ff, nodelist)
    if all([nodes, clients]):
        modified.append(
            _nodelist_dump(ff, nodes, clients)
        )

    if ff.access_for('rankfile'):
        modified.append(
            handle_rankfile(ff, nodelist)
        )

    return any(modified)

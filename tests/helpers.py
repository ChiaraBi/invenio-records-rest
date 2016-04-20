# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Helper methods for tests."""

import copy
import json
import uuid

from flask import url_for
from invenio_db import db
from invenio_pidstore import current_pidstore
from invenio_records import Record
from six.moves.urllib.parse import parse_qs, urlparse


def get_json(response):
    """Get JSON from response."""
    return json.loads(response.get_data(as_text=True))


def create_record(data):
    """Create a test record."""
    with db.session.begin_nested():
        data = copy.deepcopy(data)
        rec_uuid = uuid.uuid4()
        pid = current_pidstore.minters['recid'](rec_uuid, data)
        record = Record.create(data, id_=rec_uuid)
    return pid, record


def assert_hits_len(res, hit_length):
    """Assert number of hits."""
    assert res.status_code == 200
    assert len(get_json(res)['hits']['hits']) == hit_length


def parse_url(url):
    """Build a comparable dict from the given url.

    The resulting dict can be comparend even when url's query parameters
    are in a different order.
    """
    parsed = urlparse(url)
    return {
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'qs': parse_qs(parsed.query),
    }


def to_relative_url(url):
    """Build relative URL from external URL.

    This is needed because the test client discards query parameters on
    external urls.
    """
    parsed = urlparse(url)
    return parsed.path + '?' + '&'.join([
        '{0}={1}'.format(param, val[0]) for
        param, val in parse_qs(parsed.query).items()
    ])


def record_url(pid):
    """Get URL to a record."""
    if hasattr(pid, 'pid_value'):
        val = pid.pid_value
    else:
        val = pid

    return url_for('invenio_records_rest.recid_item', pid_value=val)

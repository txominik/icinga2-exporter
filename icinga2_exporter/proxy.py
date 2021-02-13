# -*- coding: utf-8 -*-
"""
    Copyright (C) 2019  Opsdis AB

    This file is part of icinga2-exporter.

    icinga2-exporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    icinga2-exporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with icinga2-exporter-exporter.  If not, see <http://www.gnu.org/licenses/>.

"""
import asyncio
from quart import request, Response, jsonify, Quart, Blueprint

from prometheus_client import (CONTENT_TYPE_LATEST, Counter)

from icinga2_exporter.perfdata import Perfdata
import icinga2_exporter.monitorconnection as monitorconnection
import icinga2_exporter.log as log

import re

#app = Quart( __name__)
app = Blueprint( 'icinga2',__name__)
total_requests = Counter('requests', 'Total requests to monitor-exporter endpoint')


@app.route('/', methods=['GET'])
def hello_world():
    return 'monitor-exporter alive'

@app.route("/metrics", methods=['GET'])
async def get_ametrics():
    objects = {}
    for key in request.args.keys():
        if re.match("^([^0-9]+)([0-9]+)$", key):
            r = re.search("^([^0-9]+)([0-9]+)$", key)
            if r.group(2) in objects.keys():
                objects[r.group(2)][r.group(1)] = request.args.get(key)
            else:
                objects[r.group(2)] = { r.group(1): request.args.get(key) }

    monitor_data = Perfdata(monitorconnection.MonitorConfig(), objects)

    # Fetch performance data from Monitor
    await asyncio.get_event_loop().create_task(monitor_data.get_perfdata())

    target_metrics = monitor_data.prometheus_format()
    #with open("/tmp/icinga2_exporter_targetmetrics", "a") as f:
    #    f.write(target_metrics)

    resp = Response(target_metrics)
    resp.headers['Content-Type'] = CONTENT_TYPE_LATEST
    #after_request_func(resp)
    return resp

@app.route("/health", methods=['GET'])
def get_health():
    return chech_healthy()


#@app.after_request
def after_request_func(response):
    total_requests.inc()

    call_status = {'remote_addr': request.remote_addr, 'url': request.url, 'user_agent': request.user_agent,
                   'content_length': response.content_length, 'status': response.status_code}
    log.info('Access', call_status)

    return response


def chech_healthy() -> Response:
    resp = jsonify({'status': 'ok'})
    resp.status_code = 200
    return resp


# -*- coding: utf-8 -*-

def index():
    servers = db(db.server).select(orderby=db.server.created_on)
    if not session.server: session.server = servers.first().id if servers.first() else 1
    metrics = [f.replace('_',' ').title() for f in db.reading.fields[2:-1]]
    form = SQLFORM.factory(
        Field('metric', requires=IS_IN_SET(metrics, zero=None), default = metrics[0]),
        Field('start', 'datetime'),
        Field('end', 'datetime')
        )
    return locals()

def server():
    form = crud.update(db.server, a0, deletable=False)
    if form.accepts(request.vars, session):
        s = form.vars
        return response.render('default/server_li.html', locals())
    return locals()

def server_remove():
    db(db.server.id==a0).delete()
    return ''

def set_server():
    session.server = a0
    return ''

def set_metrics():
    session.metric = request.vars.metric
    session.start = request.vars.start
    session.end = request.vars.end
    from gluon.contrib import simplejson as sj
    response.headers['Content-Type']='application/json'
    return sj.dumps([session.metric, session.start, session.end])

def get_data():
    query = (db.reading.server == (session.server or 1))
    from datetime import datetime
    format = '%Y-%m-%d %H:%M:%S'
    if session.start:
        query &= (db.reading.created_on >= datetime.strptime(session.start,format))
    if session.end:
        query &= (db.reading.created_on <=  datetime.strptime(session.end,format))
    readings = db(query).select(orderby=db.reading.created_on)
    from gluon.contrib import simplejson as sj
    import time
    metric = session.metric or "Cpu utilization"
    metric = metric.replace(' ','_').lower()
    first_reading = readings.first()
    d = dict(type= 'spline',
         name= session.metric,
         pointInterval= 5 * 60 * 1000, # five minutes //24 * 3600 *1000 //one day
         pointStart= time.mktime(first_reading.created_on.timetuple())*1000 if first_reading else 0,
         data= [r[metric] for r in readings])
    response.headers['Content-Type']='application/json'
    return sj.dumps(d)

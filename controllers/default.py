# -*- coding: utf-8 -*-

def index():
    servers = db(db.server).select(orderby=db.server.created_on)
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
        return """
<li> 
  <a class="reloader" href="%(rurl)s">%(addr)s</a> 
  <a class="undercover edit-link" href="%(eurl)s">Edit</a>
  <a class="undercover delete-link" href="%(durl)s">Remove</a>
</li> 
""" % {'addr': form.vars.address,
       'rurl': URL('set-server', args=form.vars.id),
       'eurl': URL('server', args=form.vars.id),
       'durl': URL('server_remove', args=form.vars.id)}
    return locals()

def server_remove():
    db(db.server.id==a0).delete()
    response.flash(T('Server deleted'))
    return ''

def set_server():
    session.server = a0
    return ''

def set_metrics():
    session.metric = request.vars.metric
    session.start = request.vars.start
    session.end = request.vars.end
    return ''

def get_data():
    query = db.reading.server == (session.server or 1)
    from datetime import datetime
    format = '%Y-%m-%d %H:%M:%S'
    if session.start:
        query &= (db.reading.created_on >= datetime.strptime(session.start,format))
    if session.end:
        query &= (db.reading.created_on <=  datetime.strptime(session.end,format))
    readings = db(query).select(orderby=db.reading.created_on)
    print readings
    from gluon.contrib import simplejson as sj
    import time
    metric = session.metric or "Cpu utilization"
    metric = metric.replace(' ','_').lower()
    d = dict(type= 'spline',
         name= session.metric,
         pointInterval= 5 * 60 * 1000, # five minutes //24 * 3600 *1000 //one day
         pointStart= time.mktime(readings.first().created_on.timetuple())*1000,
         data= [r[metric] for r in readings])
    response.headers['Content-Type']='application/json'
    return sj.dumps(d)

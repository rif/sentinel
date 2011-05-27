# -*- coding: utf-8 -*-

def index():
    servers = db(db.server).select(orderby=db.server.created_on)
    form = SQLFORM.factory(
        Field('metric', requires=IS_IN_SET([f.replace('_',' ').title() for f in db.reading.fields[2:-1]])),
        Field('start', 'datetime'),
        Field('end', 'datetime')
        )
    if form.accepts(request.vars, session):
        response.flash = T('Fee earner changed to %s') % db.auth_user(form.vars.fee_earner).first_name
        session.fee_earner = form.vars.fee_earner
    return locals()

def server():
    form = crud.update(db.server, a0, deletable=False)
    if form.accepts(request.vars, session):
        return """
<li> 
  <a href="%(rurl)s">%(addr)s</a> 
  <a class="undercover edit-link" href="%(eurl)s">Edit</a>
  <a class="undercover delete-link" href="%(durl)s">Remove</a>
</li> 
""" % {'addr': form.vars.address,
       'rurl': URL('reports', args=form.vars.id),
       'eurl': URL('server', args=form.vars.id),
       'durl': URL('server_remove', args=form.vars.id)}
    return locals()

def server_remove():
    db(db.server.id==a0).delete()
    response.flash(T('Server deleted'))
    return ""

def get_data():
    readings = db(db.reading.server == 1).select(orderby=db.reading.created_on)
    from gluon.contrib import simplejson as sj
    import time
    d = dict(type= 'area',
         name= 'CPU Utilization',
         pointInterval= 5 * 60 * 1000, # five minutes //24 * 3600 *1000 //one day
         pointStart= time.mktime(readings.first().created_on.timetuple())*1000,
         data= [r.cpu_utilization for r in readings])
    response.headers['Content-Type']='application/json'
    return sj.dumps(d)

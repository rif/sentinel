# -*- coding: utf-8 -*-

def index():
    servers = db(db.server).select(orderby=db.server.created_on)
    form = SQLFORM.factory(
        Field('fee_earner', default=(request.vars.fee_earner or session.fee_earner or auth.user_id))
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
    return ""

def user():
    return dict(form=auth())

def download():
    return response.download(request,db)

def call():
    session.forget()
    return service()

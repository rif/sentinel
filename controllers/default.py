# -*- coding: utf-8 -*-

def index():
    servers = db(db.server).select()
    return locals()

def server():
    form = crud.update(db.server, a0)
    return locals()

def reports():
    return locals()

def user():
    return dict(form=auth())

def download():
    return response.download(request,db)

def call():
    session.forget()
    return service()

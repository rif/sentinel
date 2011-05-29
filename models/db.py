# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('google:datastore')              # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:3ce8034e-edb1-4222-9c49-858dd4fa59f5'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
auth.settings.actions_disabled=['login','register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud


db.define_table('server',
                Field('address', requires = [IS_MATCH('^\d{1,3}(\.\d{1,3}){3}$', error_message= T('not an IP address')), IS_NOT_IN_DB(db, 'server.address')], required=True),
                Field('port', 'integer', default=22),
                Field('reader', 'string', default='rnd', requires=IS_IN_SET(('rnd','ssh','snmp'))),
                auth.signature,
                format='%(address)s')

db.define_table('reading',
                Field('server', db.server),
                Field('cpu_utilization', 'double'),
                Field('mem_total', 'double'),
                Field('mem_used', 'double'),
                Field('mem_utilization', 'double', compute=lambda r: r['mem_used']*100/r['mem_total'] if r['mem_total'] > 0 else 0),
                Field('swap_total', 'double'),
                Field('swap_used', 'double'),
                Field('swap_utilization', 'double', compute=lambda r: r['swap_used']*100/r['swap_total'] if r['swap_total'] > 0 else 0),
                Field('created_on','datetime', default=request.now))

a0,a1 = request.args(0), request.args(1)

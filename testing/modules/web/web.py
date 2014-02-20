#!/usr/bin/python

import os
from threading import Thread
from flask import Flask, render_template, flash, redirect, send_from_directory
from forms import LoginForm

class WebManager():
	
	app = Flask(__name__)
	hub = None
	
	def __init__(self, local_hub):
		global hub
		hub = local_hub
		self.app.config.update(
			CSRF_ENABLED = True,
			SECRET_KEY = '2c1de198f4d30fa5d342ab60c31eeb308b6de0f063e20efb9322940e3888d51c'
			)
			
	@app.route('/')
	@app.route('/index')
	def index():
		
		t = "--"
		h = "--"
		d = "--"
		
		if hub:
			if hub.temp_humid:
				t = hub.temp_humid.temp
				h = hub.temp_humid.humid
				d = str(hub.temp_humid.last_update)
		
			return render_template("index.html",
				title = 'Home',
				temp = t,
				humid = h,
				last_update = d
				)
        
	@app.route('/settings')
	def settings():
		return render_template("settings.html")
	
	@app.route('/gateway')
	def gateway():
		return render_template("gateway.html")


	def start(self):
		self.app.run(debug = True, host='0.0.0.0', use_reloader=False)
		
#@app.route('/login', methods = ['GET', 'POST'])
#def login():
#    form = LoginForm()
#    
#    if form.validate_on_submit():
#        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
#        print form.openid.data, form.remember_me.data
#        return redirect('/index')
#        
#    return render_template('login.html', 
#        title = 'Sign In',
#        form = form)
 
 
 
 
if __name__ == "__main__":
	#app
	wm = WebManager()
	wm.start()

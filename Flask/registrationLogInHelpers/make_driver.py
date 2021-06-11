from database import db
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models

def register():
    """
    Handles the user registering to be a driver so they can post rides
    Redirects to the post rides page with a message if successful
    """
    registerDriverForm = forms.RegisterDriverFormFactory()

    if registerDriverForm.validate_on_submit():
        netid = session['netid']
        license_no = request.form['license_no']
        license_plate_no = request.form['license_plate_no']
        plate_state = request.form['plate_state']

        #check to make sure user isn't already driver as validator so can make user driver here
        make_driver(netid, license_no, license_plate_no, plate_state)
        return redirect(url_for('rides.list_rides_main'))

    return render_template('registerLogInPages/register-driver.html', form=registerDriverForm)

def make_driver(netid, license_no, license_plate_no, plate_state):
    """
    Adds the user to database of drivers
    """
    db.session.execute('''PREPARE Register (varchar, integer, varchar, varchar) AS INSERT INTO Driver VALUES ($1, $2, $3, $4);''')
    newDriver = db.session.execute('EXECUTE Register(:netid, :license_no, :license_plate_no, :plate_state)',\
            {"netid":netid, "license_no":license_no, "license_plate_no":license_plate_no, "plate_state":plate_state})
    db.session.commit()
    db.session.execute('DEALLOCATE Register')
    session['driver'] = True
    flash("You are now a driver and can list rides.")

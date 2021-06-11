from database import db
import datetime 
from datetime import date 
from flask import Flask, request, session, flash, redirect, url_for, render_template

import forms
import models
import json

def find():
    """
    Returns results of the user searching for rides
    Doesn't show the rides the user has posted themselves or already reserved
    Makes sure there is room in the ride for the user
    """
    searchForm = forms.SearchFormFactory()
    results = []
    spots_needed=0 

    if searchForm.validate_on_submit():
        origin_city = request.form['origin_city']
        destination = request.form['destination']
        date = request.form['date']
        spots_needed = request.form['spots_needed']

        if destination == "Search All":
            results = searchAll(origin_city, date, spots_needed)
        else:
            results = search(origin_city, destination, date, spots_needed)
   
    return render_template('basicRidePages/find-rides.html', searchForm=searchForm, results=results, spots_needed=spots_needed) 

def searchAll(origin_city, date, spots_needed):
    """
    Use a prepared statement in order to find all the results with any destination that have enough spots for the request
    """
    results=[]
    db.session.execute('''PREPARE SearchAll (varchar, date, integer, varchar) AS SELECT * FROM Ride r WHERE r.origin = $1\
            AND r.date = $2 and r.seats_available >= $3 and r.driver_netid!=$4\
            AND NOT EXISTS (SELECT * FROM Reserve rev WHERE rev.ride_no=r.ride_no AND rev.rider_netid=$4);''') 
    results.extend(db.session.execute('EXECUTE SearchAll(:origin_city, :date, :spots_needed, :driver_netid)',\
                {"origin_city":origin_city, "date":date, "spots_needed":spots_needed, "driver_netid":session['netid']}))
    db.session.execute('DEALLOCATE SearchALL')
    return results

def search(origin_city, destination, date, spots_needed):
    """
    Use a prepared statement in order to find all the results with the given destination that have enough spots for the request
    """
    results=[]
    db.session.execute('''PREPARE Search (varchar, varchar, date, integer, varchar) AS SELECT * FROM Ride r\
            WHERE r.origin = $1 AND r.destination = $2 AND r.date = $3 and r.seats_available >= $4 and r.driver_netid!=$5\
            AND NOT EXISTS (SELECT * FROM Reserve rev WHERE rev.ride_no=r.ride_no AND rev.rider_netid=$5);''')
    results.extend(db.session.execute('EXECUTE Search(:origin_city, :destination, :date, :spots_needed, :driver_netid)',\
                {"origin_city":origin_city, "destination":destination, "date":date, "spots_needed":spots_needed, "driver_netid":session['netid']}))
    db.session.execute('DEALLOCATE Search')
    return results

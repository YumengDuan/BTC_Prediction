# Maria Duan, yumengdu@usc.edu
# ITP 216, Fall 2022
# Section: 31883R
# Final Project, app.py
# Description:
# Visualize and predict closing price and volume of BitCoin given relative big data from 2018 to 2023

from flask import Flask, redirect, render_template, request, session, url_for, Response, send_file
import os
import io
import sqlite3 as sl
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = "BTC.db"


# root end point
# routes to select options and the dropdown menu
@app.route("/")
def home():
    """
    Checks whether the user has selected valid options and returns appropriately.

     :return: renders home.html if selected correctly,
                redirects to client otherwise.
    """
    options = {
        "Price": "BitCoin Closing Price",
        "Volume": "BitCoin Volume"
    }
    return render_template("home.html",
                           classifications=db_get_classifications(),
                           message="Please select a classification of Bit Coin to search for.",
                           options=options)


@app.route("/submit_classification", methods=["POST"])
def submit_classification():
    """
    Receive a client POST request.

    :return: redirects to home if invalid POST request,
                redirects to classification_current otherwise.
    """
    print(request.form['classification'])
    session["classification"] = request.form["classification"]
    if 'classification' not in session or session["classification"] == "":
        return redirect(url_for("home"))
    if "data_request" not in request.form:
        return redirect(url_for("home"))
    session["data_request"] = request.form["data_request"]
    return redirect(url_for("classification_current",
                            data_request=session["data_request"],
                            classification=session["classification"]))


@app.route("/api/<data_request>/<classification>")
def classification_current(data_request, classification):
    """
    Stored values of data_request, classification,and project

    :return: render template class.html.
    """
    return render_template("class.html",
                           data_request=data_request,
                           classification=classification,
                           project=False)


@app.route("/submit_projection", methods=["POST"])
def submit_projection():
    """
    POST request received by user's input to project

    :return: redirect to home if invalid classification,
                redirect to classification_projection otherwise.
    """
    if 'classification' not in session:
        return redirect(url_for("home"))
    session["value"] = request.form["value"]
    return redirect(url_for("classification_projection",
                            data_request=session["data_request"],
                            classification=session["classification"]))


@app.route("/api/<data_request>/projection/<classification>")
def classification_projection(data_request, classification):
    """
    Project prediction with user input.

    :return: render template class.html with valid values.
    """
    return render_template("class.html",
                           data_request=data_request,
                           classification=classification,
                           project=True,
                           value=session["value"])


@app.route("/fig/<data_request>/<classification>")
def fig(data_request, classification):
    """
    Save the figure(s)

    :return: send_file image to be presented on web.
    """
    fig = create_figure(data_request, classification)
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype="image/png")


def create_figure(data_request, classification):
    """
    Create two types of figures after user's selection.

    :return: either fig
    """
    df = db_create_dataframe(classification)
    print(session)

    # to match the names between web options and dataset columns
    if data_request == "Volume":
        yaxis = "BTC_Volume"
    elif data_request == "Price":
        yaxis = "BTC_Closing"

    # First type of fig:  Volume over Date OR Price over Date, data from dataframe
    if 'value' not in session:
        # Draw the graph
        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)
        fig.suptitle("BitCoin " + data_request.capitalize() + " of " + classification + " type")
        ax.set(xlabel="Date", ylabel=data_request)
        ax.plot(df['Date'], df[yaxis].astype(float), color="purple")

        # Set up axes and labels
        year = ['2018', '2019', '2020', '2021', '2022', '2023']
        xmaxi = len(df['Date'])
        xstep = int(xmaxi // 5.3)
        ax.set_xticks(range(0, xmaxi, xstep))
        ax.set_xticklabels(year)
        ax.legend([str(data_request) + " over date"], loc=0, fontsize="10")
        fig.tight_layout()
        return fig
    # Second type of fig: Volume/Price over Value with projected data shown as well
    else:
        X = df[['Value']]
        y = df[[yaxis]]
        # Use machine learning model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict([[float(session['value'])]])

        # Draw the graph
        fig, ax = plt.subplots(1)
        fig.suptitle(classification + ' type BitCoin will have ' +
                     str(float(y_pred)) + ' ' + data_request.capitalize() + ' with given ' + session['value'])
        ax = fig.add_subplot(1, 1, 1)
        ax.set(xlabel="Value", ylabel=data_request)
        ax.scatter(df['Value'].astype(float), df[yaxis].astype(float), color="purple")
        ax.scatter(float(session['value']), float(y_pred), color="green")
        ax.legend(["Existing data", "Prediction"], loc=0, fontsize="10")
        fig.tight_layout()
        plt.show()
        return fig


def db_create_dataframe(classification):
    """
    Turn a database into a dataframe

    :return: dataframe
    """
    conn = sl.connect(db)
    curs = conn.cursor()

    table = "BTC_Price_Volume"
    stmt = "SELECT * from " + table + " where `Value_Classification`=?"
    data = curs.execute(stmt, (classification,))
    df = pd.DataFrame(curs.fetchall(), columns=['Date', 'Value', 'Value_Classification', 'BTC_Closing', 'BTC_Volume'])
    conn.close()
    return df


def db_get_classifications():
    """
    From the table get classification

    :return: classification
    """
    conn = sl.connect(db)
    curs = conn.cursor()

    table = "BTC_Price_Volume"
    stmt = "SELECT `Value_Classification` from " + table
    data = curs.execute(stmt)
    # sort a set comprehension for unique values
    classification = sorted({result[0] for result in data if result[0] != ''})
    conn.close()
    return classification


@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for("home"))


# unit tests
# def test(data_request, classification):
#     df = db_create_dataframe(classification)
#     if data_request == "Volume":
#         yaxis = "BTC_Volume"
#     elif data_request == "Price":
#         yaxis = "BTC_Closing"
#
#     # fig, ax = plt.subplots(1)
#     # fig.suptitle("BitCoin " + data_request.capitalize() + " of " + classification + " type")
#     # ax.set(xlabel="Year", ylabel=data_request)
#     # ax.plot(df['Date'], df[yaxis].astype(float), color="purple")
#     # year = ['2018', '2019', '2020', '2021', '2022', '2023']
#     # xmaxi = len(df['Date'])
#     # xstep = int(xmaxi // 5.3)
#     # print(xmaxi)
#     # print(xstep)
#     # ax.set_xticks(range(0, xmaxi, xstep))
#     # ax.set_xticklabels(year)
#     # fig.tight_layout()
#     # plt.show()
#
#     X = df[['Value']]
#     y = df[[yaxis]]
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     model = LinearRegression()
#     model.fit(X_train, y_train)
#     a = 100
#     y_pred = model.predict([[a]])
#     fig, ax = plt.subplots(1)
#     fig.suptitle('BitCoin of type ' + "classification" + ' will have ' +
#                  str(float(y_pred)) + ' ' + "data_request.capitalize()" + ' with given value of ' + "session['value']")
#     ax = fig.add_subplot(1, 1, 1)
#     ax.set(xlabel="Value", ylabel=data_request)
#     ax.scatter(df['Value'].astype(float), df[yaxis].astype(float), color="purple")
#     ax.scatter(a, float(y_pred), color="green")
#     ax.legend(["Existing data", "Prediction"], loc=0, fontsize="10")
#     fig.tight_layout()
#     plt.show()


if __name__ == "__main__":
    # print(test("Volume", "Greed"))
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=1235)

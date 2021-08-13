"""
GEOCODER STEPS:
this is a Flask app, expects from the user a CSV file, it has to have a "Address" column. Recognise address lower/upper.
On the main page it is written:
"                                        Super Geocoder
Please upload your .csv file. The values containing addresses should be in a column named address or Address
[button:"Chose file"] _____(name of the file______[button: "Submit"]                            "

When you press "Submit", you get the table shown below with the same CSV but with added latitude/longitude columns,
according to the addresses. Bellow you have a "Download" button, a file is downloaded.

If there is no address column, you should write below "Please make sure you have an address column in your CSV file!"
__________________________________________-
STEPS:
1. creating the directories
2. creating basic HTML with CSS
3. create the python file with a decorators and very simple functions that do nothing
    1-index, stays simple
    2-success, we need "POST"
    3-download, to send file
    (every time the user does something, you make a decorator)
4. in the 2)"success" we add code, we check if we have post, then we get the file (request.files with a name of
    the input). When the user presses "submit" button in HTML, the URL triggers "success" function.
    We create DF, we apply geocode to created columns, with lambda function we create LON,LAT
    With "drop" we remove unnecessary columns, we put that to CSV ()to_csv with some name)
5. in HTML we need to have the placeholder for:
    1-HTML string   {{ ??? }}
    2-HTML template {% ??? %}   (the extension appears on every page, but here we have to ignore missing, today:
                                if btn...include btn...endif)
6. create a "download.html" for the download button, when the button is pressed, it activates the URL to "download"
    function, there we can download the file (send file as attachment)
7. check if there is an "address" column, it could be fone with IF or TRY/EXCEPT (better), if for any reason we upload
    a file that could not be red, than it will be informed, so creating a dataframe is inside and the rest of the code.
    We return the index.html with a text (table), and a button
    In the except part, we put different return, index.html, with different text (Error explanation)
8. (extra) using datetime creating a unique filename to save and download

"""

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pandas import read_csv, DataFrame
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim



app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/success', methods=['POST'])
def success():
    global file
    if request.method=='POST':
        file=request.files["mirko-file"]

        df = read_csv(file)
        df.head()

        if ("Address" or "address") in df:
            geolocator = Nominatim(user_agent="mirko-app")

            # 1 - conveneint function to delay between geocoding calls
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.2)
            # 2- - create location column
            df['location'] = df['Address'].apply(geocode)
            # 3 - create longitude, laatitude and altitude from location column (returns tuple)
            df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
            # 4 - split point column into latitude, longitude and altitude columns
            df[['latitude', 'longitude', 'altitude']] = DataFrame(df['point'].tolist(), index=df.index)
            print(df)
            df = df.drop(['location', 'point', 'altitude', df.columns[0]], axis=1)
            df.to_csv(secure_filename("uploaded"+file.filename))

            return render_template("index.html", tables=[df.to_html(classes='data')], titles=df.columns.values, btn="download.html")
        return render_template("index.html", text="Please make sure you have an address column in your CSV file!")


@app.route("/download")
def download():
    return send_file("uploaded"+file.filename, attachment_filename="yourfile.csv", as_attachment=True)


if __name__=="__main__":
    app.debug=True
    app.run(port=5000)
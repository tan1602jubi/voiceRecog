import pymongo
import threading
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request, render_template, jsonify
import json
import re

app = Flask(__name__)

bikeDetails = {"Please help me with the Make,Model and Variant of your bike, Your bike registration number and year of manufacture. (You can say something like Bajaj Pulsar 180cc MH03CQ9771 2016)": {},
                "Next I would need the color of the two wheeler and year of registration (You can say something like Black 2017)": {},
                "We are almost done, I would like to know if there are any electrical accessories, side car, LPG/CNG fitted in your two wheeler.Kindly only spell out those which are present and if none of them are relevant just say none. (Eg: side car, lpg, cng and electrical accessories or None)": {},
                "Lastly I would want to know the base IDV and Total IDV(You can say something like 45000, 53200":{}}   

bikeQues = 0

@app.route('/voiceRecog', methods=['GET', 'POST'])
def home1():
    global bikeQues
    bikeQues = -1
    return render_template('index.html', name='index')

@app.route('/', methods=['GET', 'POST'])
def home():
    global bikeQues
    bikeQues = -1
    return render_template('index2.html', name='index2')

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def getDetails(usrStr, queNum):
    d = {}
    print(usrStr, "------", queNum)
    tw_df = pd.read_csv("./static/tw_Desc.csv")
    place_df = pd.read_csv("./static/place.csv")
    colors = ['ALUMINUM', 'BEIGE', 'BLACK', 'BLUE', 'BROWN', 'BRONZE', 'CLARET', 'COPPER', 'CREAM', 'GOLD', 'GRAY', 'GREEN', 'MAROON', 'METALLIC', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'RED', 'ROSE', 'RUST', 'SILVER', 'TAN', 'TURQUOISE', 'WHITE', 'YELLOW']
    if queNum == "first" or queNum == 1:
        r = "[A-Z]{2}[0-9]{1,2}(?:[A-Z])?(?:[A-Z]*)?[0-9]{4}" 
        
        f = open("./static/two_wheel.json")
        data = json.load(f)
        m = [i for i in list(data.keys()) if re.search(i, usrStr)]
        print(m)
        if len([i for i in list(data.keys()) if re.search(i, usrStr)]) > 0:
            # make = list(set(l) & set(list(data.keys())))[0]
            make = [i for i in list(data.keys()) if re.search(i, usrStr)][0]
            usrStr = usrStr.replace(make, "")
            d["make"] = make
            print(list(data[make].keys()))

            if len([i for i in list(data[make].keys()) if re.search(i, usrStr)]) > 0:
                # model = list(set(l) & set(list(data[make].keys())))[0]
                d["model"] = [i for i in list(data[make].keys()) if re.search(i, usrStr)][0]
                model = d["model"]
                usrStr = usrStr.replace(d["model"], "")
                try:
                    varient = [i for i in data[make][model] if re.search(str(i).replace(" ", "").upper(), usrStr.replace(" ", "").upper())]
                    d["Varient"] = max(varient)
                    usrStr = usrStr.replace(d["Varient"], "")
                except Exception as er:
                    d["Varient"] = "---"
                    print(er)
        try:
            d["regNum"] = re.search(r, usrStr.replace(" ", "")).group()
            usrStr = usrStr.replace(" ", "").replace(d["regNum"], "")
        except Exception as er:
            d["regNum"] = "---"
            print(er)

        try:
            d["year of manufacturer"] = re.search("[0-9]{4}", usrStr).group()
        except Exception as er:
            d["year of manufacturer"] = "---"
            print(er)    
        try:
            ft = tw_df.loc[(tw_df["MANUFACTURE"]==make) & (tw_df["MODEL"] == model) & (tw_df["VARIANT"] == d["Varient"])]
            print(ft)
            d["Fuel Type"] = list(ft.FUEL)[0]
            d["Cubic Capacity"] = list(ft.CC)[0]
            d["SEATING_CAPACITY"] = list(ft.SEATING_CAPACITY)[0]
        except Exception as er:
            d["Fuel Type"] = "---"
            d["Cubic Capacity"] = "---"
            d["SEATING_CAPACITY"] = "---"
            print(er)

        try:
            pl = place_df.loc[(place_df["RTA_CODE"] == d["regNum"][:4])]
            d["Place of Registration"] = list(pl.RTA_LOC_NAME)[0]
        except Exception as er:
            d["Place of Registration"] = "---"
            print(er)    

    if queNum == "second" or queNum == 2:
        try:
            d["color"] = [i for i in colors if re.search(i, usrStr)][0]
            usrStr = usrStr.replace(d["color"], "")
            d["year of registration"] = re.search("[0-9]{4}", usrStr).group()
        except Exception as er:
            print(er)
    if queNum == "third" or queNum == 3:
        try:     
            d["side car"] = re.search("SIDE CAR", usrStr).group()
            d["side car"] = "Yes"
        except:
            d["side car"] = "NA"
        try:    
            d["lpg"] = re.search("LPG", usrStr).group()
            d["lpg"] = "Yes"
        except:
            d["lpg"] = "NA"
        try:        
            d["cng"] = re.search("CNG", usrStr).group()
            d["cng"] = "Yes"
        except:
            d["cng"] = "NA" 

        try:
            d["electrical accessories"] = re.search("ELECTRICAL", usrStr).group()      
            d["electrical accessories"] = "Yes"
        except:
            d["electrical accessories"] = "NA"    

    if queNum == "fourth" or queNum == 4:

        l = usrStr.split(" ")
        try:
            idv = [int(i) for i in l if re.search("[0-9]+", i)]
            d["idv"] = min(idv)
            d["total idv"] = max(idv)
        except:
            d["idv"] = "NA"        
    print("Str", usrStr)
    print ("Detailssssss", d)        
    return d

@app.route("/usrSays", methods=['POST'])
def userSays():
    global bikeDetails, bikeQues
    data = dict(request.form)
    res = "How can I help you..!"
    print(data)
    if data["usrSays"] == "bike details":
        bikeQues += 1
        print(bikeQues,"PPP")
        print(list(bikeDetails.keys())[bikeQues])
        res = list(bikeDetails.keys())[bikeQues]
        bikeQues += 1
    elif bikeQues < 5 and bikeQues >= 0:
        bikeDetails[list(bikeDetails.keys())[bikeQues-1]] = getDetails(data["usrSays"].upper(), bikeQues)
        try:
            res = list(bikeDetails.keys())[bikeQues]
            bikeQues += 1
        except Exception as er:
            table = '<p>Here is what extracted..!</p><br><table class="table table-dark"><thead><tr><th scope="col">#</th><th scope="col">Fields</th> <th scope="col">Values</th></tr></thead><tbody>'
            tableContent = {}
            for i in bikeDetails:
                for j in bikeDetails[i]:
                    tableContent[j] = bikeDetails[i][j]
            c = 1
            print(tableContent)
            for i in tableContent:
                table += '<tr><th scope="row">'+str(c)+'</th><td>'+str(i)+'</td><td>'+str(tableContent[i])+'</td></tr>'
                c += 1
            table += '</tbody></table>'    
            res = table 
            bikeQues = -1      
    else:
        bikeQues = -1 
        print(bikeDetails)    
    return jsonify(res=res) 

@app.route("/firstPost", methods=['POST'])
def firstPost():
    model = request.get_json()
    print(model)
    details = getDetails(model["data"].upper(), model["stage"])
    model["tags"]["details"] = {}
    model["tags"]["details"] = details
    model["stage"] = "second"
    print(model, "modellllllllllllllllllllllllll")
    return jsonify(model)

@app.route("/secondPost", methods=['POST'])
def secondPost():
    model = request.get_json()
    print(model, "modelllllllllllllllllllllllllllllllll")
    details = getDetails(model["data"].upper(), model["stage"])
    details = merge_two_dicts(details, model["tags"]["details"])
    model["tags"]["details"] = details
    model["stage"] = "third"
    return jsonify(model)

@app.route("/thirdPost", methods=['POST'])
def thirdPost():
    model = request.get_json()

    details = getDetails(model["data"].upper(), model["stage"])
    details = merge_two_dicts(details, model["tags"]["details"])
    model["tags"]["details"] = details
    model["stage"] = "final"
    return jsonify(model)   

@app.route("/finalPre", methods=['POST'])
def finalPre():
    model = request.get_json()
    print(model["tags"]["details"])
    alldetails = ""
    for i in model["tags"]["details"]:
        alldetails += "<b>" + i + "</b>: "+ model["tags"]["model"][i] + "<br>"

    model["reply"]={"type" : "text",
                    "text" : alldetails,}    

    details = getDetails(model["data"].upper(), model["stage"])
    details = merge_two_dicts(details, model["tags"]["details"])
    model["tags"]["details"] = details
    model["stage"] = "final"
    return jsonify(model)

# @app.route("/firstPre", methods=['POST'])
# def firstPre():
#     print(request)
#     model = request.get_json()

#     details = getDetails(model["data"], bikeQues)
#     model["tags"]["details"] = {}
#     model["tags"]["details"] = getDetails(model["data"], model["stage"])
#     model["stage"] = "second"
#     return jsonify(str(model), 200)

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))    
    app.run(host='0.0.0.0', port=port, threaded = True)
    #app.run_server(host='0.0.0.0', port=port,threaded = True)
    #app.run(host='0.0.0.0')
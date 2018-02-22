

from flask import Flask , request, send_from_directory, jsonify
from urllib import urlencode
from urlparse import parse_qs, urlsplit, urlunsplit
from flask import session

app = Flask(__name__ , static_url_path='')
from flask import jsonify

import requests
#from requests.packages.urllib3.poolmanager import PoolManager
from urllib3.poolmanager import PoolManager
import json
import base64
import uuid
import string
import urllib
import urlparse
import ssl
#import backports.ssl as ssl
import config
import urllib2


configuration = config.applicationConfig()
createPaymentPayloadTemplate = config.getSetExpressCheckoutTemplate()
getPaymentDetailsTemplate = config.getGetEcPaymentPayloadTemplate()
doECPaymentDetailsTemplate = config.getDoEcPaymentPayloadTemplate()

class MyAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            #ssl_version=ssl.PROTOCOL_TLSv1_2,
        )
        print("poolmanager set")



@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route("/")
def root():
	return app.send_static_file('index.html')
@app.route("/available")
def available():
	itemjson={};
	f=open("items.txt","r") 
	results = map(int, f.read().split(","))
	itemjson['items']=results
	#session['items']=itemjson['items']
	return jsonify(itemjson);

def constructQueryParam(urlString, paramName, paramvalue):
	try:
		paramName = '='+str(paramName)
		paramvalue = '='+str(paramvalue)
		if(paramName in urlString):
			new_url = urlString.replace(paramName, paramvalue)
		else:
			new_url = urlString + "&"+paramName+paramvalue
		return new_url
	except Exception as err:
		print err
		return "error"
		

		
@app.route("/CreatePayment",methods=['POST','OPTIONS']) 
def createPayment():
	try:

		postData = request.get_json()
		print postData;
		url = configuration['URL']
		stringPayload = createPaymentPayloadTemplate
		
		payloadData = ""
		payloadData = constructQueryParam(stringPayload, 'METHOD', configuration['SetEC_METHOD'])
		payloadData = constructQueryParam(payloadData, 'USER', configuration['USER'])
		payloadData = constructQueryParam(payloadData, 'PWD', configuration['PWD'])
		payloadData = constructQueryParam(payloadData, 'SIGNATURE', configuration['SIGNATURE'])

		payloadData = constructQueryParam(payloadData, 'RETURNURL', request.url_root+configuration["RETURN_URL"])
		payloadData = constructQueryParam(payloadData, 'CANCELURL', request.url_root+configuration["CANCEL_URL"])

		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_PAYMENTACTION', configuration['ACTION'])

		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_CURRENCYCODE', postData['currency'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_AMT', postData['total'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_ITEMAMT', postData['price'])
		payloadData = constructQueryParam(payloadData, 'L_PAYMENTREQUEST_0_NAME0', postData['name'])
		
		payloadData = constructQueryParam(payloadData, 'L_PAYMENTREQUEST_0_QTY0', postData['quantity'])
		payloadData = constructQueryParam(payloadData, 'L_PAYMENTREQUEST_0_AMT0', postData['subtotal'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_INSURANCEAMT', postData['insurance'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_TAXAMT', postData['tax'])

		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPDISCAMT', postData['shipping_discount'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_HANDLINGAMT', postData['handling_fee'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPPINGAMT', postData['shipping'])
		payloadData = constructQueryParam(payloadData, 'BUTTONSOURCE', configuration['BN_CODE'])
		payloadData = constructQueryParam(payloadData, 'VERSION', configuration['VERSION'])

	

		if(postData["customFlag"]=="true"):
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTONAME', postData['recipient_name'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOSTREET', postData['line1'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOSTREET2', postData['line2'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOCITY', postData['city'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOSTATE', postData['state'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOZIP', postData['postal_code'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE', postData['country_code'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME', postData['country_code'])
			payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_SHIPTOPHONENUM', postData['phone'])

		
	
		headers = {
			'cache-control': "no-cache",
			}

		_requests = requests.Session()
		_requests.mount(url, MyAdapter())
		response = _requests.post(url, data = payloadData, headers=headers)
		unquoted = urllib.unquote(response.text)
		print response.text
		return unquoted
	except Exception as err:
		print err
		return "error"


@app.route("/GetEcPayment",methods=['POST','OPTIONS']) 
def GetEcPayment():
	try:
		
		postData = request.get_json()
		url = configuration['URL']
		stringPayload = getPaymentDetailsTemplate
		payloadData = ""
		payloadData = constructQueryParam(stringPayload, 'METHOD', configuration['GetEC_METHOD'])
		payloadData = constructQueryParam(payloadData, 'USER', configuration['USER'])
		payloadData = constructQueryParam(payloadData, 'PWD', configuration['PWD'])
		payloadData = constructQueryParam(payloadData, 'SIGNATURE', configuration['SIGNATURE'])
		payloadData = constructQueryParam(payloadData, 'TOKEN', postData["paymentToken"])
		payloadData = constructQueryParam(payloadData, 'VERSION', configuration['VERSION'])
		headers = {
			'cache-control': "no-cache",
			}
		_requests = requests.Session()
		_requests.mount(url, MyAdapter())
		response = _requests.post(url, data = payloadData, headers=headers)
		unquoted = urllib.unquote(response.text)
		return unquoted
	except Exception as err:
		print err
		return "error"

@app.route("/ExecutePayments",methods=['POST','OPTIONS']) 
def executePayment():
	try:
		postData = request.get_json()
		print postData
		print 'amr'
		token = postData['paymentToken']
		payerId = postData['payerID']
		
		url = configuration['URL']
		stringPayload = doECPaymentDetailsTemplate;
		payloadData = ""
		payloadData = constructQueryParam(stringPayload, 'METHOD', configuration['DoEC_METHOD'])
		payloadData = constructQueryParam(payloadData, 'TOKEN', postData["paymentToken"])
		payloadData = constructQueryParam(payloadData, 'PAYERID', postData["payerID"])
		payloadData = constructQueryParam(payloadData, 'USER', configuration['USER'])
		payloadData = constructQueryParam(payloadData, 'PWD', configuration['PWD'])
		payloadData = constructQueryParam(payloadData, 'SIGNATURE', configuration['SIGNATURE'])
		payloadData = constructQueryParam(payloadData, 'VERSION', configuration['VERSION'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_PAYMENTACTION', configuration['ACTION'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_AMT', postData['total'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_CURRENCYCODE', postData['currency'])
		payloadData = constructQueryParam(payloadData, 'PAYMENTREQUEST_0_ITEMAMT', postData['total'])
		payloadData = constructQueryParam(payloadData, 'L_PAYMENTREQUEST_0_NAME0', postData['name'])
		payloadData = constructQueryParam(payloadData, 'L_PAYMENTREQUEST_0_AMT0', postData['total'])
			
		items=postData['description']
		print items
		itemarr=map(int, items.split(","))		
		res=[0,0,0,0,0]
		f=open("items.txt","r") 
		itemFromFile=f.read().split(",")
		itemFromFileint = map(int, itemFromFile)		
		print itemFromFileint
		print 'hello1'
		i=0
		print 'hello2'
		for item in itemFromFileint:
			print 'hello3'
			res[i]=itemFromFileint[i]-itemarr[i]
			i+=1	
		print 'hello'
		resStr=map(str, res)
		file = open("items.txt", "w")
		file.write(','.join(resStr));
		file.close()
		print 'itemarr'
		print itemarr
		headers = {
			'content-type': "application/json",
			'PayPal-Partner-Attribution-Id' : configuration['BN_CODE']
			}
		_requests = requests.Session()
		_requests.mount(url, MyAdapter())
		response =  _requests.post(url, data=payloadData, headers=headers)
		unquoted = urllib.unquote(response.text)
		return unquoted
	except Exception as err:
		print err
		return "error"

@app.route("/successPayment", methods=['GET','OPTIONS']) 
def showSuccessPage():
	query_string = request.query_string
	if ('false'=='false'):
		return app.send_static_file('failure.html')
	return app.send_static_file('success.html')

@app.route("/cancelUrl", methods=['GET','OPTIONS']) 
def showCancelPage():
	return app.send_static_file('cancel.html')

@app.route("/successPayment", methods=['POST','OPTIONS']) 
def showSuccessPageData():
	try:
		query_string = request.query_string 
		token = request.args.get('token')
		url = configuration['URL']

		stringPayload = getPaymentDetailsTemplate
		payloadData = ""
		payloadData = constructQueryParam(stringPayload, 'METHOD', configuration['GetEC_METHOD'])
		payloadData = constructQueryParam(payloadData, 'USER', configuration['USER'])
		payloadData = constructQueryParam(payloadData, 'PWD', configuration['PWD'])
		payloadData = constructQueryParam(payloadData, 'SIGNATURE', configuration['SIGNATURE'])
		payloadData = constructQueryParam(payloadData, 'TOKEN', token)
		payloadData = constructQueryParam(payloadData, 'VERSION', configuration['VERSION'])
	
		headers = {
			'cache-control': "no-cache",
			'PayPal-Partner-Attribution-Id' : configuration['BN_CODE']
			}
		_requests = requests.Session()
		_requests.mount(url, MyAdapter())
		response = _requests.post(url, data=payloadData, headers=headers)
		return response.text
	except Exception as err:
		return "error"



app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == '__main__':
   app.run(host='10.21.62.92',port=8080,debug = True)

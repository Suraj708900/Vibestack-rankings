import json,secrets,concurrent.futures
from pathlib import Path
import urllib.request,urllib.error,types
class Response:
 def __init__(self,r):self.status_code=r.code;self.headers=r.headers;self.data=r.read()
 def json(self):return json.loads(self.data)
class Session:
 def __init__(self):self.headers={}
 def _call(self,method,url,body=None,headers=None,timeout=45):
  h={**self.headers,**(headers or {})};data=None
  if body is not None:data=json.dumps(body).encode();h['Content-Type']='application/json'
  req=urllib.request.Request(url,data=data,headers=h,method=method)
  try:return Response(urllib.request.urlopen(req,timeout=timeout))
  except urllib.error.HTTPError as e:return Response(e)
 def post(self,url,json=None,headers=None,timeout=45):return self._call('POST',url,json,headers,timeout)
 def get(self,url,timeout=45):return self._call('GET',url,timeout=timeout)
requests=types.SimpleNamespace(Session=Session)
B=Path(__file__).resolve().parent;root='https://preview.aiuseflow.com/checkout-repair-v1';session=requests.Session();session.headers.update({'Origin':'https://preview.aiuseflow.com','User-Agent':'AIUseFlow-Integration-QA/1.0'})
checks=[]
def check(name,ok):
 checks.append({'name':name,'passed':bool(ok)});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def post(d):
 r=session.post(root+'/api/checkout.php',json=d,timeout=45)
 try:j=r.json()
 except Exception:raise RuntimeError('Non-JSON response: '+str(r.status_code))
 return r,j
nonce=secrets.token_hex(16)
base={'action':'create','product':'ai-learning-kit','method':'upi','name':'AIUseFlow QA TEST — no payment','email':'contact@aiuseflow.com','request_id':nonce,'company':'','amount':0.01}
r,j=post(base);check('Order is saved before payment, in isolated sandbox',r.status_code==200 and j.get('sandbox') is True and j.get('status')=='awaiting_payment')
if r.status_code!=200:print(j);raise SystemExit(1)
check('Server ignores client-supplied amount',float(j['amount'])==199.0)
check('Notifications honestly labelled sandbox',j.get('notifications')=={'owner':'sandbox','customer':'sandbox'})
check('UPI contains order ID and authoritative amount',j['id'] in j['upi_url'] and 'am=199.00' in j['upi_url'])
access={'id':j['id'],'access_key':j['access_key']};(B/'test-access.private.json').write_text(json.dumps(access));(B/'test-access.private.json').chmod(0o600)
r,j2=post(base);check('Create retries return same tracking ID',j2.get('id')==access['id'])
r,wrong=post({'action':'status','id':access['id'],'access_key':'0'*64});check('Wrong tracking key is rejected without customer details',r.status_code==404 and 'email' not in wrong)
r,s=post({'action':'status',**access});check('Tracking response excludes email, name, UTR and file paths',r.status_code==200 and not any(k in s for k in ['email','name','utr','file','track_hash','access_key']))
check('Tracking is not cached',r.headers.get('Cache-Control')=='no-store')
r,invalid=post({'action':'proof',**access,'method':'upi','utr':'123'});check('Invalid transaction reference rejected',r.status_code==400)
r,proof=post({'action':'proof',**access,'method':'upi','utr':'123456789012'});check('Payment reference saved without falsely confirming payment',r.status_code==200 and proof.get('status')=='submitted')
r,again=post({'action':'proof',**access,'method':'upi','utr':'123456789012'});check('Duplicate payment submission is idempotent',r.status_code==200 and again.get('status')=='submitted')
r,changed=post({'action':'proof',**access,'method':'upi','utr':'999999999999'});check('Replacing a submitted payment reference is blocked',r.status_code==409)
r,status=post({'action':'status',**access});check('Tracking updates to pending verification',status.get('status')=='submitted')
r=session.get(root+'/api/checkout.php',timeout=45);check('Checkout mutation cannot be requested by GET',r.status_code==405)
r=session.post(root+'/api/checkout.php',json={'action':'status',**access},headers={'Origin':'https://untrusted.example'},timeout=45);check('Cross-origin request rejected',r.status_code==403)
r=session.get(root+'/api/notifications.php',timeout=45);check('Notification administration requires existing admin access',r.status_code==401)
r=session.post(root+'/api/contact.php',json={'name':'Checkout QA TEST','email':'contact@aiuseflow.com','subject':'general','message':'TEST ONLY — isolated contact form verification, no customer enquiry.','website':'','elapsed':5000,'lang':'en'},timeout=45)
try:contact=r.json()
except Exception:contact={}
check('Contact message saved with reference ID in sandbox',r.status_code==200 and bool(contact.get('id')) and contact.get('notifications',{}).get('owner')=='sandbox')
result={'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'checks':checks,'real_payment_submitted':False,'production_orders_modified':False}
(B/'backend-test-results.json').write_text(json.dumps(result,indent=2));print(json.dumps({'passed':result['passed'],'failed':result['failed']}),flush=True)
raise SystemExit(bool(result['failed']))

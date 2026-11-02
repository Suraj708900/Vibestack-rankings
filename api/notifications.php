<?php
require __DIR__.'/_boot.php';require __DIR__.'/_notifications.php';
header('Cache-Control: no-store');header('X-Robots-Tag: noindex');
if(!vs_is_admin())vs_send_json(401,['error'=>'Unauthorized.']);
if(!in_array(vs_method(),['GET','POST'],true))vs_send_json(405,['error'=>'Method not allowed.']);
if(vs_method()==='POST'&&(!vs_same_origin()||vs_rate_limited('notification-retry',10,3600)))vs_send_json(403,['error'=>'Retry not allowed.']);
$pending=0;$sent=0;$failed=0;$retried=0;
foreach(glob(auf_notice_dir().'/*.json')?:[] as $p){$j=json_decode(file_get_contents($p),true);if(($j['state']??'')==='sent'){$sent++;continue;}$pending++;if(($j['attempts']??0)>=8)$failed++;
 if(vs_method()==='POST'&&$retried<10&&($j['next']??0)<=time()&&($j['attempts']??0)<8){auf_notice_flush(basename($p,'.json'));$retried++;}
}
vs_send_json(200,['ok'=>true,'pending'=>$pending,'accepted_by_provider'=>$sent,'exhausted_retries'=>$failed,'retried'=>$retried]);

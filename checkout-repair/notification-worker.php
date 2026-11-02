<?php
// Run from Hostinger cron every five minutes. Not callable through the web.
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
require __DIR__.'/_boot.php';require __DIR__.'/_notifications.php';
$count=0;$sent=0;foreach(glob(auf_notice_dir().'/*.json')?:[] as $p){$j=json_decode(file_get_contents($p),true);if(($j['state']??'')!=='pending'||($j['next']??0)>time()||($j['attempts']??0)>=8)continue;$r=auf_notice_flush(basename($p,'.json'));$count++;if($r['state']==='sent')$sent++;if($count>=10)break;}
echo json_encode(['attempted'=>$count,'accepted_by_provider'=>$sent])."\n";

<?php
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
$pub=dirname(__DIR__);$zip=$pub.'/.private/aiuseflow-v4-staging.zip';
$target=$pub.'/preview/smart-tools-v4';
if (is_file($target.'/.auf-owned')) { echo json_encode(['status'=>'already-staged']);exit; }
if (file_exists($target)) throw new RuntimeException('Target already exists; refusing overwrite.');
if (hash_file('sha256',$zip)!=='c559497515dfa9b15ea10d168cac835422a21c4da56325a0e56767cac05f4256') throw new RuntimeException('Package checksum mismatch');
$z=new ZipArchive();if($z->open($zip,ZipArchive::CHECKCONS)!==true) throw new RuntimeException('Invalid zip');
for($i=0;$i<$z->numFiles;$i++){$n=$z->getNameIndex($i);if(str_contains($n,'..')||str_starts_with($n,'/')||str_contains($n,'\\')||preg_match('/\.(php|sql|sqlite|env)$/i',$n))throw new RuntimeException('Unsafe entry');}
mkdir($target,0755,true);if(!$z->extractTo($target))throw new RuntimeException('Extract failed');$entries=$z->numFiles;$z->close();
file_put_contents($target.'/.auf-owned','AIUseFlow staging only 20261101');
if(!is_file($target.'/tools/index.html')||!is_file($target.'/assets/app.js'))throw new RuntimeException('Missing entrypoints');
echo json_encode(['status'=>'staged','entries'=>$entries,'prefix'=>'/smart-tools-v4/','production_app_changed'=>false]);

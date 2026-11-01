<?php
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
$pub=dirname(__DIR__);$target=$pub.'/preview/smart-tools-v4';$archive=$pub.'/.private/aiuseflow-v4-patch.zip';
$expected='ff777d9c77a0cc7154387b2646e7f295a78b3d4e7a5efd63d9ea0a18494418d9';$marker=$pub.'/.private/v4-patch-'.substr($expected,0,12).'.done';
if(is_file($marker)){echo file_get_contents($marker);exit;}
if(!is_file($target.'/.auf-owned'))throw new RuntimeException('Staging ownership marker missing');
if(hash_file('sha256',$archive)!==$expected)throw new RuntimeException('Checksum mismatch');
$z=new ZipArchive();if($z->open($archive,ZipArchive::CHECKCONS)!==true)throw new RuntimeException('Invalid archive');
$backup=dirname($pub).'/v4-backups-20261101/staging-patch-'.substr($expected,0,12).'.zip';$b=new ZipArchive();$b->open($backup,ZipArchive::CREATE);
for($i=0;$i<$z->numFiles;$i++){$n=$z->getNameIndex($i);if(str_contains($n,'..')||str_starts_with($n,'/')||str_contains($n,'\\')||preg_match('/\.(php|sql|sqlite|env)$/i',$n))throw new RuntimeException('Unsafe path');if(is_file($target.'/'.$n))$b->addFile($target.'/'.$n,$n);}
$b->close();chmod($backup,0600);
if(!$z->extractTo($target))throw new RuntimeException('Extract failed');
$out=json_encode(['status'=>'staging-updated','files'=>$z->numFiles,'sha256'=>$expected,'production_app_changed'=>false]);file_put_contents($marker,$out);echo $out;

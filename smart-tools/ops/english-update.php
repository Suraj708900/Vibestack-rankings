<?php
declare(strict_types=1);
if(PHP_SAPI!=='cli'){http_response_code(404);exit;}
$stage=($argv[1]??'')==='stage';$tag=$stage?'english-stage':'english-live';$pub=dirname(__DIR__);$root=$stage?$pub.'/preview/smart-tools-v4':$pub;
$cfg=json_decode(file_get_contents(__DIR__.'/'.$tag.'.json'),true,512,JSON_THROW_ON_ERROR);$archive=__DIR__.'/'.$tag.'.zip';$marker=__DIR__.'/'.$tag.'-'.substr($cfg['sha256'],0,12).'.done';
if(is_file($marker)){echo file_get_contents($marker);exit;}
if($stage&&!is_file($root.'/.auf-owned'))throw new RuntimeException('Staging ownership unavailable');
if(!$stage&&!is_file(__DIR__.'/v4-live-approved.done'))throw new RuntimeException('Expected production release unavailable');
$lock=fopen(__DIR__.'/maintenance-state/lock','c');if(!flock($lock,LOCK_EX|LOCK_NB))throw new RuntimeException('Maintenance busy; no changes');
$original=[];$created=[];$started=false;
function putAtomic(string $p,string $b):void{if(!is_dir(dirname($p)))mkdir(dirname($p),0755,true);$t=tempnam(dirname($p),'.auf-update-');if(file_put_contents($t,$b)!==strlen($b))throw new RuntimeException('Write failed');chmod($t,0644);if(!rename($t,$p))throw new RuntimeException('Atomic update failed');}
try{
 if(hash_file('sha256',$archive)!==$cfg['sha256'])throw new RuntimeException('Archive checksum mismatch');$z=new ZipArchive();if($z->open($archive,ZipArchive::CHECKCONS)!==true)throw new RuntimeException('Invalid archive');
 if($z->numFiles!==count($cfg['files']))throw new RuntimeException('Unexpected file count');
 foreach($cfg['files'] as $n=>$hash){if(str_contains($n,'..')||str_starts_with($n,'/')||str_contains($n,'\\')||!preg_match($stage?'~^(assets/|tools/|qa\.html$)~':'~^(assets/smart-tools-v4/|tools/)~',$n)||preg_match('/\.(php|sql|env|sqlite)$/i',$n))throw new RuntimeException('Path outside module');$p=$root;foreach(explode('/',$n) as $part){$p.='/'.$part;if(is_link($p))throw new RuntimeException('Symlink refused');}if($hash['before']!==null){if(!is_file($p)||hash_file('sha256',$p)!==$hash['before'])throw new RuntimeException('Intervening file change: '.$n);$original[$n]=file_get_contents($p);}elseif(file_exists($p))throw new RuntimeException('New path conflict: '.$n);if(hash('sha256',$z->getFromName($n))!==$hash['after'])throw new RuntimeException('Entry checksum mismatch');}
 if(!$stage)$original['search-index.json']=file_get_contents($root.'/search-index.json');
 $backup=dirname($pub).'/v4-release-backups/'.$tag.'-'.substr($cfg['sha256'],0,12);mkdir($backup,0700,true);$bp=$backup.'/before-update.zip';$b=new ZipArchive();$b->open($bp,ZipArchive::CREATE);foreach($original as $n=>$data)$b->addFromString($n,$data);$b->close();chmod($bp,0600);
 if($b->open($bp,ZipArchive::CHECKCONS)!==true)throw new RuntimeException('Backup open failed');$restored=0;foreach($original as $n=>$data){$r=$b->getFromName($n);if($r===false||hash('sha256',$r)!==hash('sha256',$data))throw new RuntimeException('Backup restore verification failed');$s=$b->statName($n);if(hash('crc32b',$r)!==sprintf('%08x',$s['crc']))throw new RuntimeException('Backup CRC mismatch');$restored++;}$b->close();
 $files=$cfg['files'];uksort($files,fn($a,$b)=>(str_ends_with($a,'.html')<=>str_ends_with($b,'.html'))?:strcmp($a,$b));$started=true;
 foreach($files as $n=>$hash){if(!isset($original[$n]))$created[]=$n;putAtomic($root.'/'.$n,$z->getFromName($n));}
 if(!$stage){$rows=json_decode($original['search-index.json'],true,512,JSON_THROW_ON_ERROR);foreach($rows as &$row)if(($row['u']??'')==='/tools/')$row['d']='50 useful tools for PDFs, images, invoices, writing and SEO. Free browser utilities, no login for basics, English interface.';unset($row);putAtomic($root.'/search-index.json',json_encode($rows,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE|JSON_THROW_ON_ERROR)."\n");}
 foreach($cfg['files'] as $n=>$hash)if(hash_file('sha256',$root.'/'.$n)!==$hash['after'])throw new RuntimeException('Installed file hash mismatch');
 $out=['status'=>$stage?'staging-updated':'production-updated','interface'=>'English only','files'=>count($cfg['files']),'backup_restore_entries'=>$restored,'backup_sha256'=>hash_file('sha256',$bp),'time'=>gmdate('c'),'database_changed'=>false];file_put_contents($marker,json_encode($out));chmod($marker,0600);echo json_encode($out)."\n";
}catch(Throwable $e){if($started){foreach($original as $n=>$data)putAtomic($root.'/'.$n,$data);foreach($created as $n)if(is_file($root.'/'.$n))unlink($root.'/'.$n);}fwrite(STDERR,'Update stopped: '.$e->getMessage().($started?' (rolled back)':' (no module changes)')."\n");exit(1);}

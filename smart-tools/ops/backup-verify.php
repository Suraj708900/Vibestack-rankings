<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
set_time_limit(0);
$pub=dirname(__DIR__); // Uploaded as public_html/.private/v4-backup-verify.php.
$domain=dirname($pub);$dest=$domain.'/v4-backups-20261101';
if(!is_dir($dest))mkdir($dest,0700,true);
$lock=fopen($dest.'/lock','c');if(!flock($lock,LOCK_EX|LOCK_NB))exit("Backup already running.\n");
if(is_file($dest.'/verified.json')){echo file_get_contents($dest.'/verified.json')."\n";exit;}
try{
 if(!class_exists('ZipArchive'))throw new RuntimeException('PHP ZIP extension unavailable');
 $sql=$pub.'/.private/v4-backup/mysql-export.sql';
 if(!is_file($sql)||hash_file('sha256',$sql)!=='b0b3f65e09e91a917f54d0ab1c0e953f6e63e03e395aa79f8658ffc14e42644e')throw new RuntimeException('SQL backup missing or checksum mismatch');
 if(!copy($sql,$dest.'/mysql-export.sql'))throw new RuntimeException('Cannot protect SQL export');chmod($dest.'/mysql-export.sql',0600);
 $sqlText=(string)file_get_contents($sql);$tables=preg_match_all('/CREATE TABLE/',$sqlText);if($tables!==21||!str_contains($sqlText,'COMMIT;'))throw new RuntimeException('SQL structure validation failed');unset($sqlText);
 $files=[];$links=[];$snapshots=[];
 foreach(['public_html','blog','private'] as $dir){
  $base=$domain.'/'.$dir;if(!is_dir($base)||is_link($base))continue;
  $it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($base,FilesystemIterator::SKIP_DOTS));
  foreach($it as $f){$path=$f->getPathname();$rel=substr($path,strlen($domain)+1);
   if($f->isLink()){$links[$rel]=readlink($path);continue;}
   if(!$f->isFile()||str_starts_with($rel,'public_html/.private/v4-backup/'))continue;
   $files[$rel]=$path;
   if(preg_match('/\.(sqlite|db)$/i',$path)){
    $fh=fopen($path,'rb');$head=fread($fh,16);fclose($fh);
    if($head!=="SQLite format 3\0")continue;
    $snap=$dest.'/sqlite-snapshots/'.$rel;if(!is_dir(dirname($snap)))mkdir(dirname($snap),0700,true);
    if(class_exists('SQLite3')){$src=new SQLite3($path,SQLITE3_OPEN_READONLY);$to=new SQLite3($snap);if(!$src->backup($to))throw new RuntimeException('SQLite consistent backup failed');$to->close();$src->close();}
    else {$db=new PDO('sqlite:'.$path);$db->exec('VACUUM INTO '.$db->quote($snap));$db=null;}
    $db=new PDO('sqlite:'.$snap);if($db->query('PRAGMA integrity_check')->fetchColumn()!=='ok')throw new RuntimeException('SQLite integrity check failed');$db=null;
    $files[$rel]=$snap;$snapshots[]=$rel;
   }
  }
 }
 foreach($snapshots as $s){unset($files[$s.'-wal'],$files[$s.'-shm']);}
 ksort($files);$zipPath=$dest.'/aiuseflow-4-full-before-upgrade.zip';
 $zip=new ZipArchive();if($zip->open($zipPath,ZipArchive::CREATE|ZipArchive::OVERWRITE)!==true)throw new RuntimeException('Cannot create archive');
 foreach($files as $rel=>$file)if(!$zip->addFile($file,$rel))throw new RuntimeException('Archive add failed');
 $zip->addFile($dest.'/mysql-export.sql','database/mysql-export.sql');
 $zip->addFromString('backup-manifest.json',json_encode(['time'=>gmdate('c'),'files'=>count($files),'sqlite_snapshots'=>count($snapshots),'mysql_tables'=>$tables,'symlinks'=>$links],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));
 if(!$zip->close())throw new RuntimeException('Archive finalization failed');chmod($zipPath,0600);
 if($zip->open($zipPath,ZipArchive::CHECKCONS)!==true)throw new RuntimeException('Archive consistency failed');
 $count=$zip->numFiles;$total=0;
 for($i=0;$i<$count;$i++){
  $st=$zip->statIndex($i);$name=$st['name'];if(str_starts_with($name,'/')||str_contains($name,'..')||str_contains($name,'\\'))throw new RuntimeException('Unsafe archive entry');
  $stream=$zip->getStream($name);if(!$stream)throw new RuntimeException('Cannot read archive entry');$crc=hash_init('crc32b');$bytes=0;
  while(!feof($stream)){$chunk=fread($stream,1048576);if($chunk===false)throw new RuntimeException('Archive read failed');hash_update($crc,$chunk);$bytes+=strlen($chunk);}fclose($stream);
  if(hash_final($crc)!==sprintf('%08x',$st['crc'])||$bytes!==$st['size'])throw new RuntimeException('Archive CRC verification failed');$total+=$bytes;
 }
 $restore=$dest.'/restore-check';if(!is_dir($restore))mkdir($restore,0700,true);
 if(!$zip->extractTo($restore))throw new RuntimeException('Restore test extraction failed');$zip->close();
 foreach(['public_html/index.html','public_html/.htaccess','database/mysql-export.sql'] as $check)if(!is_file($restore.'/'.$check))throw new RuntimeException('Restore missing critical file');
 if(hash_file('sha256',$restore.'/database/mysql-export.sql')!==hash_file('sha256',$dest.'/mysql-export.sql'))throw new RuntimeException('SQL restore checksum failed');
 $report=['status'=>'verified','time'=>gmdate('c'),'archive'=>'v4-backups-20261101/aiuseflow-4-full-before-upgrade.zip','archive_bytes'=>filesize($zipPath),'archive_sha256'=>hash_file('sha256',$zipPath),'entries_crc_verified'=>$count,'uncompressed_bytes'=>$total,'all_entries_restored'=>true,'mysql_export_tables'=>$tables,'sqlite_integrity_checked'=>count($snapshots),'symlinks_recorded'=>count($links),'mysql_import_test'=>'pending separate isolated import'];
 file_put_contents($dest.'/verified.json',json_encode($report,JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));chmod($dest.'/verified.json',0600);echo json_encode($report,JSON_UNESCAPED_SLASHES)."\n";
}catch(Throwable $e){fwrite(STDERR,'Backup failed: '.$e->getMessage()."\n");exit(1);}
